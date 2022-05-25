function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function autoTransition() {
  await pageChange("/next");
}

async function pageChange(direction) {
  var blinking = document.getElementById("fadein");
  blinking.id = "fadeout";
  await sleep(1850);
  window.location.href = window.location.origin + direction;
}

document.addEventListener("keydown", async function (event) {
  if (event.key === "ArrowRight") {
    await pageChange("/next");
  } else if (event.key === "ArrowLeft") {
    await pageChange("/prev");
  } else if (event.key === "ArrowUp") {
    window.location.href = window.location.origin + "/config/";
  }
});

var xDown = null;
var yDown = null;

function getTouches(event) {
  return event.touches || event.originalEvent.touches;
}

document.addEventListener("touchstart", function (event) {
  xDown = getTouches(event)[0].clientX;
  yDown = getTouches(event)[0].clientY;
});

document.addEventListener("touchend", async function (event) {
  if (!xDown || !yDown) {
    return;
  }

  var xDiff = xDown - event.changedTouches[0].clientX;
  var yDiff = yDown - event.changedTouches[0].clientY;

  if (Math.abs(xDiff) > Math.abs(yDiff)) {
    /*most significant*/
    if (xDiff > 0) {
      console.log("Right Swipe");
      await pageChange("/next");
    } else {
      console.log("Left Swipe");
      await pageChange("/prev");
    }
  } else {
    if (yDiff > 0) {
      console.log("Down Swipe");
    } else {
      window.location.href = window.location.origin + "/config/";
    }
  }
  /* reset values */
  xDown = null;
  yDown = null;
});
