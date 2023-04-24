document.addEventListener("DOMContentLoaded", function () {
  function createBookCard(book) {
    // This is how the book card will be dynamically created and displayed on the webpage. The book card will be created using the book object passed as an argument to this function.
    // You can use the book object to get the book's title, author, image, description, etc.
    // You can also use the book object to get the book's id and use it to create the link to the book details page.

    const bookCard = document.createElement("div");
    bookCard.classList.add("book-card");

    const contentWrapper = document.createElement("div");
    contentWrapper.classList.add("content-wrapper");

    const bookImage = document.createElement("img");
    bookImage.classList.add("book-card-img");
    bookImage.src = book.volumeInfo.imageLinks.thumbnail;
    bookImage.alt = "";
    if (book.volumeInfo.imageLinks && book.volumeInfo.imageLinks.thumbnail) {
      bookImage.src = book.volumeInfo.imageLinks.thumbnail;
    } else {
      bookImage.src =
        "https://media.istockphoto.com/id/157181664/photo/ornate-old-book-cover.jpg?s=612x612&w=0&k=20&c=miwxfzz5SZBkr4Ae3nJ1KXgsuE7Z6JFLqIQkHNMgDRQ=";
    }

    const cardContent = document.createElement("div");
    cardContent.classList.add("card-content");

    const bookTitle = document.createElement("div");
    bookTitle.classList.add("book-name");
    bookTitle.textContent = book.volumeInfo.title;

    const bookAuthor = document.createElement("div");
    bookAuthor.classList.add("book-by");
    if (book.volumeInfo.authors) {
      bookAuthor.textContent = "by " + book.volumeInfo.authors.join(", ");
    } else {
      bookAuthor.textContent = "by Unknown Author";
    }

    const bookSummary = document.createElement("div");
    bookSummary.classList.add("book-sum", "card-sum");
    bookSummary.textContent = book.volumeInfo.description;

    cardContent.appendChild(bookTitle);
    cardContent.appendChild(bookAuthor);
    // cardContent.appendChild(ratingSection);
    cardContent.appendChild(bookSummary);

    contentWrapper.appendChild(bookImage);
    contentWrapper.appendChild(cardContent);

    bookCard.appendChild(contentWrapper);
    const likeProfile = document.createElement("div");
    likeProfile.classList.add("like-profile");

    const likeName = document.createElement("div");
    likeName.classList.add("like-name");

    const detailswrapper = document.createElement("div");
    detailswrapper.classList.add("details-wrapper");

    const exploreSpan = document.createElement("span");
    exploreSpan.textContent = "Explore Details";

    const exploreLink = document.createElement("a");
    exploreLink.href = `/book_details/${book.id}`; // Replace with the correct URL pattern for your book details page
    exploreLink.textContent = "  HERE";

    detailswrapper.appendChild(exploreSpan);
    detailswrapper.appendChild(exploreLink);

    likeName.appendChild(detailswrapper);

    bookCard.appendChild(contentWrapper);
    bookCard.appendChild(likeProfile);
    bookCard.appendChild(likeName);

    return bookCard;
  }

  // get all the book type buttons which are the genre buttons on the homepage
  const bookTypes = document.querySelectorAll(".book-type");

  // function to load the most popular books
  function loadMostPopularBooks() {
    // make an axios request to get the most popular books. we use the /most_popular_books_json endpoint for this.
    // once we get the response, we will loop through the books and create a book card for each book using the createBookCard function.
    // this way we can dynamically create the book cards and display them on the homepage.
    axios
      .get("/most_popular_books_json")
      .then((response) => {
        const books = response.data;
        const bookCards = document.querySelector(".book-cards");
        bookCards.innerHTML = "";
        books.forEach((book) => {
          const bookCard = createBookCard(book);
          bookCards.appendChild(bookCard);
        });
      })
      .catch((error) => {
        console.log(error);
      });
  }

  // all genres button event listener
  const allGenresButton = document.querySelector(".book-type.active");
  // if the all genres button exists, add an event listener to it. This prevents the event listener from being added when the all genres button is not present on the page.
  if (allGenresButton) {
    allGenresButton.addEventListener("click", (e) => {
      // using this event listener we are toggling the active class on the all genres button.
      e.preventDefault();
      // if the all genres button is not active, make it active and remove the active class from the other genre buttons.
      if (!allGenresButton.classList.contains("active")) {
        allGenresButton.classList.add("active");
        bookTypes.forEach((bookType) => {
          // make sure the all genres button is not removed from the active class
          if (bookType !== allGenresButton) {
            bookType.classList.remove("active");
          }
        });
        loadMostPopularBooks();
      }
    });
  }

  // other genre buttons event listeners
  bookTypes.forEach((bookType) => {
    bookType.addEventListener("click", (e) => {
      e.preventDefault();
      // if the genre button is not active, make it active and remove the active class from the other genre buttons.
      if (!bookType.classList.contains("active")) {
        bookType.classList.add("active");
        bookTypes.forEach((otherBookType) => {
          if (otherBookType !== bookType) {
            otherBookType.classList.remove("active");
          }
        });
        const genre = bookType.textContent.trim();
        //  make an axios request to get the books by genre. we use the /books_by_genre_json endpoint for this.
        // once we get the response, we will loop through the books and create a book card for each book using the createBookCard function.
        axios
          .get(`/books_by_genre_json/${genre}`)
          .then((response) => {
            const books = response.data;
            const bookCards = document.querySelector(".book-cards");
            bookCards.innerHTML = "";
            books.forEach((book) => {
              const bookCard = createBookCard(book);
              bookCards.appendChild(bookCard);
            });
          })
          .catch((error) => {
            console.log(error);
          });
      }
    });
  });

  bookTypes.forEach((bookType) => {
    bookType.addEventListener("click", (e) => {
      e.preventDefault();

      // remove active class from all book types
      bookTypes.forEach((bookType) => {
        bookType.classList.remove("active");
      });

      // add active class to the clicked book type
      e.target.classList.add("active");
    });
  });

  // profile menu dropdown
  // Add the "click" event listener to the document
  document.addEventListener("click", (event) => {
    // Check if the clicked element is the profile menu or a child of it
    const profileMenu = document.querySelector(".profile-menu");
    const dropdownContent = profileMenu.querySelector(".dropdown-content");

    if (profileMenu.contains(event.target)) {
      // Toggle the "show" class on the dropdown content
      dropdownContent.classList.toggle("show");
      console.log("clicked");
    } else {
      // Remove the "show" class from the dropdown content
      dropdownContent.classList.remove("show");
    }
  });

  // Close the dropdown if the user clicks outside of it
  window.onclick = function (event) {
    if (!event.target.matches(".profile-menu")) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      for (var i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains("show")) {
          openDropdown.classList.remove("show");
        }
      }
    }
  };
});
