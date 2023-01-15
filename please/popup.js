chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.command == "data") {
      document.getElementById("loading").style.display = "none";
      if (request.data){
          document.getElementById("content").innerHTML = request.data.message;
      }
      document.getElementById("status").innerHTML = `Response status code: ${request.status}`;
    }
  });
  