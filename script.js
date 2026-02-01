document.querySelectorAll(".clickable").forEach(card => {
  card.addEventListener("click", () => {
    card.classList.toggle("active");
  });
});
