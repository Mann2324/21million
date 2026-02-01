// Reveal animation
const reveals = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("active");
    }
  });
});

reveals.forEach(el => observer.observe(el));

// Line Chart
new Chart(document.getElementById("lineChart"), {
  type: "line",
  data: {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [{
      label: "Network Activity",
      data: [120, 190, 300, 250, 400],
      borderColor: "#22c55e",
      backgroundColor: "rgba(34,197,94,0.1)"
    }]
  }
});

// Pie Chart
new Chart(document.getElementById("pieChart"), {
  type: "pie",
  data: {
    labels: ["BTC", "ETH", "Stable", "Others"],
    datasets: [{
      data: [42, 31, 19, 8],
      backgroundColor: ["#22c55e", "#4ade80", "#86efac", "#bbf7d0"]
    }]
  }
});
