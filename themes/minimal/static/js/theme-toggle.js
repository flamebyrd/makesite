//Check for saved theme when the page loads. Placed outside the event listener to prevent FOUC
if(localStorage.getItem("theme")){
  loadTheme( localStorage.getItem("theme") );
}

function loadTheme( theme ) {
  switch ( theme ) {
    case 'dark':
      document.getElementById('dark-theme-import').disabled = true;
      document.getElementById('dark-theme-stylesheet').disabled = false;
      document.getElementById('dark-theme-stylesheet').setAttribute('media', 
      'all');
      localStorage.setItem('theme', 'dark');
      break;
    case 'light': 
      document.getElementById('dark-theme-import').disabled = true;
      document.getElementById('dark-theme-stylesheet').disabled = true;
      document.getElementById('dark-theme-stylesheet').setAttribute('media', 
      'none');
      localStorage.setItem('theme', 'light');
      break;
  }
}

document.addEventListener("DOMContentLoaded", function(){
  //identify the toggle switch HTML element
  var toggleSwitch = document.getElementById('theme-toggle-button');
  
  if (localStorage.getItem("theme")) {
    toggleSwitch.setAttribute('data-current-theme', localStorage.getItem("theme") );
  }
  else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    toggleSwitch.setAttribute('data-current-theme', 'dark');
  }
  else {
    toggleSwitch.setAttribute('data-current-theme', 'light');
  }

  //function that changes the theme, and sets a localStorage variable to track the theme between page loads
  function switchTheme(e) {

    switch ( toggleSwitch.getAttribute( 'data-current-theme' ) ) {
      case 'dark':
        toggleSwitch.setAttribute('data-current-theme', 'light');
        loadTheme('light');
        break;
      default: 
        toggleSwitch.setAttribute('data-current-theme', 'dark');
        loadTheme('dark');
        break;
    }   
  }

  //listener for changing themes
  toggleSwitch.addEventListener('click', switchTheme, false);

});