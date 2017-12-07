(function($) {
  "use strict"; // Start of use strict

  // Smooth scrolling using jQuery easing
  $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      if (target.length) {
        $('html, body').animate({
          scrollTop: (target.offset().top - 54)
        }, 1000, "easeInOutExpo");
        return false;
      }
    }
  });

  // Closes responsive menu when a scroll trigger link is clicked
  $('.js-scroll-trigger').click(function() {
    $('.navbar-collapse').collapse('hide');
  });

  // Activate scrollspy to add active class to navbar items on scroll
  $('body').scrollspy({
    target: '#mainNav',
    offset: 54
  });

  // Collapse the navbar when page is scrolled
  $(window).scroll(function() {
    if ($("#mainNav").offset().top > 100) {
      $("#mainNav").addClass("navbar-shrink");
    } else {
      $("#mainNav").removeClass("navbar-shrink");
    }
  });

})(jQuery); // End of use strict

// fetch() returns a promise
var decoder = new TextDecoder();
fetch("http://127.0.0.1:8000/catstream").then(response => {
  // response.body is a readable stream.
  // Calling getReader() gives access to the stream's content
  var reader = response.body.getReader();
  // read() returns a promise that resolves when a value has been received
  return reader.read().then(function processResult(result) {
    // Result objects contain two properties:
    // done  - true/false, and value - the data
    if (result.done) {
      return;
    }
    // result.value is a Uint8Array, we need to decode it
    var chunk = decoder.decode(result.value, {stream: true});
    var lines = chunk.split('\n');
    lines.forEach(function(text) {
      if(text.length === 0) {
        return
      }
      var obj = JSON.parse(text);
      // set element attributes
      var element = document.querySelector('.cat-gallery .portfolio-item.hide');
      var next_element = element.cloneNode(true);
      // add placeholder for a next cat
      document.querySelector('.cat-gallery').appendChild(next_element);

      // process and unhide the current cat
      element.querySelector('.cat-image').setAttribute('src', obj.image);
      element.querySelector('.cat-name').textContent = obj.name;
      element.querySelector('.cat-price').textContent = obj.price;
      element.classList.add('show');
      element.classList.remove('hide');
    });
    // Read some more, and call this function again
    return reader.read().then(processResult);
  });
});
