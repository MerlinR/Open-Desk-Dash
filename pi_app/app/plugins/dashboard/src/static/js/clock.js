function GenTime() {
  // Creating object of the Date class
  var date = new Date();
  var hour = date.getHours();
  var minute = date.getMinutes();
  var period = "";

  if (hour >= 12) {
    period = "PM";
  } else {
    period = "AM";
  }

  if (hour == 0) {
    hour = 12;
  } else {
    if (hour > 12) {
      hour = hour - 12;
    }
  }

  hour = update(hour);
  minute = update(minute);

  document.getElementById("digital-clock").innerText =
    hour + " : " + minute + " " + period;
  setTimeout(GenTime, 2000);
}

function GenDate() {
  // Creating object of the Date class
  var date = new Date();
  var day = date.getDay();
  var month = date.getMonth();
  var year = date.getFullYear();

  day = update(day);
  month = update(month);

  document.getElementById("digital-date").innerText =
    day + "-" + month + "-" + year;
  setTimeout(GenDate, 2000);
}

function update(t) {
  if (t < 10) {
    return "0" + t;
  } else {
    return t;
  }
}

GenTime();
GenDate();
