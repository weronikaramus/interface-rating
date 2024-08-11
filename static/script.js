function showRatingForm() {
  var ratingForm = document.getElementById("ratingForm");
  if (ratingForm.style.display === "none") {
    ratingForm.style.display = "block";
  } else {
    ratingForm.style.display = "none";
  }
}


function showInstruction() {
  var instruction = document.getElementById("instruction");
  var button = document.getElementById("showInstruction");
  if (instruction.style.display === "none") {
    instruction.style.display = "flex";
    button.innerHTML = 'x';
  } else {
    instruction.style.display = "none";
    button.innerHTML = '?';
  }
}

function showAverage(){
  var average = document.getElementById("averageRating");
  if (average.style.display === "none") {
    average.style.display = "flex";
  } else {
    average.style.display = "none";
  }
}

const submitButton = document.getElementById('rate');
submitButton.addEventListener('click',showAverage);