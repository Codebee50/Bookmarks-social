const siteUrl = "//codebee.com:8000/";
const styleUrl = siteUrl + "static/css/bookmarklet.css";
const minWidth = 250;
const minHeight = 250;

//load css
let head = document.getElementsByTagName("head")[0];
let link = document.createElement("link");
link.rel = "stylesheet";
link.type = "text/css";
link.href = styleUrl + "?r=" + Math.floor(Math.random() * 99999999999999);
head.appendChild(link);

//load HTML
let body = document.getElementsByTagName("body")[0];
let boxHtml = `
<div id="bookmarklet">
 <a href="#" id="close">&times;</a>
 <h1>Select an image to bookmark:</h1>
 <div class="images"></div>
 </div>
`;
body.innerHTML += boxHtml;

function bookmarkletLaunch() {
  let bookmarklet = document.getElementById("bookmarklet");
  let imagesFound = bookmarklet.querySelector(".images");

  //clear images found
  imagesFound.innerHTML = "";

  //displaybookmarlet
  bookmarklet.style.display = "block";

  // close event
  bookmarklet.querySelector("#close").addEventListener("click", function () {
    bookmarklet.style.display = "none";
  });

  //find images in the dom with minimum dimensions
  images = document.querySelectorAll('img[src$=".jpg"], img[src$=".jpeg"], img[src$=".png"]')//getting all img elements whose src attributes finishes with .jpg or .jpeg
  images.forEach(image => {
    if(image.naturalWidth >= minWidth && image.naturalHeight >= minHeight){
        let imageFound = document.createElement('img');
        imageFound.src = image.src;
        imagesFound.append(imageFound)
    } 
  })

    //select image event
  imagesFound.querySelectorAll('img').forEach(image=> {
    image.addEventListener('click', function(event){
      console.log('clicked')
        let imageSelected = event.target;
        bookmarklet.style.display = 'none'
        window.open(siteUrl + 'images/create/?url=' + encodeURIComponent(imageSelected.src)+'&title='+encodeURIComponent(document.title), '_blank')
    })
  })
}




//launch the bookmarlet 
bookmarkletLaunch()
