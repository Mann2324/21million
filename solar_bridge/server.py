import asyncio
import json
import os
import struct
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "10000"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def checksum_response(frame: bytes) -> int:
    return sum(frame[1:-2]) & 0xFF


def build_logger_response(request: bytes) -> bytes | None:
    # LSW3 Server-B handshake response used by established LSW3 server implementations.
    if len(request) < 12 or request[0] != 0xA5:
        return None
    try:
        response = bytearray(23)
        response[0] = 0xA5
        response[1:3] = (10).to_bytes(2, "little")
        response[3] = 0x10
        # Echo the request type with the response offset used by the LSW3 protocol.
        response[4] = max(0, min(255, request[4] - 0x30))
        response[5] = 0 if request[5] >= 0xFF else request[5] + 1
        response[6] = request[6]
        response[7:11] = request[7:11]
        response[11] = request[11]
        response[12] = 0x01
        timestamp = int(time.time())
        response[13:17] = timestamp.to_bytes(4, "big")
        response[17] = 0x78
        response[18:21] = b"\x00\x00\x00"
        response[21] = checksum_response(response)
        response[22] = 0x15
        return bytes(response)
    except Exception:
        return None


def extract_frames(buffer: bytearray):
    frames = []
    while True:
        start = buffer.find(b"\xA5")
        if start < 0:
            buffer.clear()
            break
        if start:
            del buffer[:start]
        if len(buffer) < 3:
            break
        payload_len = int.from_bytes(buffer[1:3], "little")
        total_len = payload_len + 17
        if total_len < 17 or total_len > 4096:
            del buffer[0]
            continue
        if len(buffer) < total_len:
            break
        frame = bytes(buffer[:total_len])
        del buffer[:total_len]
        frames.append(frame)
    return frames


def parse_frame(frame: bytes):
    result = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "length": len(frame),
        "hex": frame.hex(),
    }
    if len(frame) >= 11 and frame[0] == 0xA5:
        result["control_code"] = frame[3] | (frame[4] << 8)
        result["sequence"] = frame[5] | (frame[6] << 8)
        result["logger_serial"] = int.from_bytes(frame[7:11], "little")
    return result


def supabase_insert(table: str, row: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "Supabase environment variables are not configured"
    body = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{table}",
        data=body,
        method="POST",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return 200 <= response.status < 300, response.status
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:500]}"
    except Exception as exc:
        return False, str(exc)


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    print(f"[CONNECT] {peer}", flush=True)
    buffer = bytearray()
    try:
        while True:
            chunk = await reader.read(4096)
            if not chunk:
                break
            buffer.extend(chunk)
            for frame in extract_frames(buffer):
                info = parse_frame(frame)
                print(
                    f"[FRAME] serial={info.get('logger_serial')} control=0x{info.get('control_code', 0):04x} length={info['length']}",
                    flush=True,
                )

                # Send the protocol response immediately so the logger can continue.
                response = build_logger_response(frame)
                if response:
                    writer.write(response)
                    await writer.drain()

                # Keep raw V5 packets in Supabase while we validate the exact
                # telemetry frame layout of this logger firmware.
                ok, detail = await asyncio.to_thread(supabase_insert, "solar_frames", info)
                if not ok:
                    print(f"[SUPABASE] {detail}", flush=True)
                else:
                    print("[SUPABASE] frame stored", flush=True)
    except Exception as exc:
        print(f"[ERROR] {peer}: {exc}", flush=True)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        print(f"[DISCONNECT] {peer}", flush=True)


async def main():
    print("==============================================")
    print(" SOFAR LSW3 CLOUD BRIDGE")
    print("==============================================")
    print(f"Listening on {HOST}:{PORT}")
    print(f"Supabase configured: {bool(SUPABASE_URL and SUPABASE_KEY)}")
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
