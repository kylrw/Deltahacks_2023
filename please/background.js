chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.command == "selected-tab") {
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          let currentUrl = tabs[0].url;
          fetch('http://127.0.0.1:5000/fakeblock', {
              method: 'POST',
              body: JSON.stringify({ url: currentUrl }),
              headers: { 'Content-Type': 'application/json' },
          })
          .then((response) => {
              if (response.ok) {
                  return response.json();
              }
              throw new Error('Error: ' + response.status);
          })
          .then((data) => {
              chrome.runtime.sendMessage({ command: "data", data: data, status: 200 });
          })
          .catch((error) => {
              chrome.runtime.sendMessage({ command: "data", data: error.message, status: error.status });
          });
      });
    }
  });
  