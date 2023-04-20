const searchInput = document.getElementById("search-input");

searchInput.addEventListener("focus", () => {
  searchInput.style.width = "200px";
});

searchInput.addEventListener("blur", () => {
  searchInput.style.width = "inital";
});

const favoriteForms = document.querySelectorAll(".favorite-form");
favoriteForms.forEach((form) => {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    axios
      .post(form.action)
      .then((response) => {
        location.reload();
      })
      .catch(function (error) {
        console.log(error);
      });
  });
});
