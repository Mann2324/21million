let price = 0.012;
let holders = 1200;
const supply = 21000000;

const priceEl = document.getElementById("price");
const changeEl = document.getElementById("change");
const holdersEl = document.getElementById("holders");
const marketcapEl = document.getElementById("marketcap");

const ctx = document.getElementById('priceChart');

let labels = [];
let data = [];

const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: labels,
    datasets: [{
      data: data,
      borderColor: '#7c8cff',
      borderWidth: 2,
      tension: 0.4
    }]
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { x: { display: false }, y: { display: false } }
  }
});

function updatePrice() {
  let oldPrice = price;
  let move = (Math.random() - 0.45) * 0.002;
  price += move;
  if (price < 0.002) price = 0.002;

  let change = ((price - oldPrice) / oldPrice) * 100;

  priceEl.textContent = price.toFixed(4);
  changeEl.textContent = `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`;
  changeEl.style.color = change >= 0 ? "#22c55e" : "#ef4444";

  holders += Math.floor(Math.random() * 2);
  holdersEl.textContent = holders.toLocaleString();

  marketcapEl.textContent =
    "$" + Math.floor(price * supply).toLocaleString();

  labels.push("");
  data.push(price.toFixed(4));
  if (data.length > 30) {
    data.shift();
    labels.shift();
  }

  chart.update();
}

setInterval(updatePrice, 2000);
