function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pageChange(direction, ms) {
  var blinking = document.getElementById("fadein");
  blinking.id = "fadeout";
  await sleep(ms);
  window.location.href = window.location.origin + direction;
}

document.addEventListener("keydown", async function (event) {
  if (event.key === "ArrowRight") {
    await pageChange("/next", 850);
  } else if (event.key === "ArrowLeft") {
    await pageChange("/prev", 850);
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
      await pageChange("/next", 850);
    } else {
      console.log("Left Swipe");
      await pageChange("/prev", 850);
    }
  } else {
    if (yDiff > 0) {
      console.log("Down Swipe");
    } else {
      console.log("Up Swipe");
    }
  }
  /* reset values */
  xDown = null;
  yDown = null;
});
