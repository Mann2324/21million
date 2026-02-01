// BASE VALUES
let price = 0.0125;        // starting price
let holders = 1250;
const totalSupply = 21000000;

// PRICE UPDATE (every 2 seconds)
function updatePrice() {
  let volatility = (Math.random() * 0.002) - 0.001; // small up/down
  let trend = 0.00015; // upward bias

  price = price + volatility + trend;

  if (price < 0.001) price = 0.001;

  document.getElementById("price").innerText = price.toFixed(4);

  // MARKET CAP
  let marketCap = (price * totalSupply).toFixed(0);
  document.getElementById("marketcap").innerText =
    "$" + marketCap.toLocaleString();
}

// HOLDERS GROWTH
function updateHolders() {
  holders += Math.floor(Math.random() * 3); // slow organic growth
  document.getElementById("holders").innerText =
    holders.toLocaleString();
}

// COUNT-UP ANIMATION
function animateSupply() {
  let count = 0;
  let interval = setInterval(() => {
    count += 210000;
    document.getElementById("supply").innerText =
      count.toLocaleString();

    if (count >= totalSupply) {
      document.getElementById("supply").innerText =
        totalSupply.toLocaleString();
      clearInterval(interval);
    }
  }, 50);
}

// RUN
animateSupply();
setInterval(updatePrice, 2000);
setInterval(updateHolders, 3000);
