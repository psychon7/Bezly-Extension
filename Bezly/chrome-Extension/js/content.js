chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log("Got a request")
    if (request.inputFieldId) {
      var inputField = document.getElementById(request.inputFieldId);
      if (inputField) {
        sendResponse(inputField.value);
      } else {
        sendResponse(null);
      }
    }
  });