document.addEventListener("DOMContentLoaded", function() {
    var element = document.getElementById("signout");
    element.addEventListener("click", function() {
      // Do something when the element is clicked
      chrome.storage.sync.set({'auth': ''}, function() {
        console.log('Settings saved');
    });
      window.location.replace("./login.html")
    });
});