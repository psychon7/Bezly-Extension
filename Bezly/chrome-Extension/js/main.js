window.onload = function(){
    console.log("Windows Loadeds")
    var auths = '';
    chrome.storage.sync.set({'foo': 'hello', 'bar': 'hi'}, function() {
        console.log('Settings saved');
    });

    document.getElementById("prof").addEventListener('click', function(){
        window.location.replace("./profile.html")
    })
    
    chrome.storage.sync.get(['auth'], function(items) {
        console.log(items.auth)
        if(items.auth == undefined || items.auth == null || items.auth == ''){
            console.log("No auth Found");
            window.location.replace("./login.html")
        }

        auths = items.auth
        Getredits(items.auth)
    });

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var currentUrl = tabs[0].url;
        const match = currentUrl.match(/https?:\/\/(.*\.amazon\.[a-z]+)\/(.*)\/dp\/(.*)/i);
        if (!match) {
            window.location.replace("./error.html")
        } else {
            const website = match[1];
            const nameAndASIN = match[3];
            const index = nameAndASIN.indexOf('/');
            const ASIN = getASIN(currentUrl);
            const regex = /\/([A-Za-z0-9\-]+)\/([A-Za-z0-9]+)\//;
            const matchn = regex.exec(currentUrl);

            // If the URL doesn't match the expected pattern, return null
            if (!matchn) {
                return null;
            }

            // Extract the product name and return it
            const productName = matchn[1];
            console.log('Website:', website);
            console.log('Product Name:', productName);
            console.log('ASIN:', ASIN);
            GetAIResponse(website, productName, ASIN, auths)
        }
    });

    var element = document.getElementById("opaci");
    element.style.opacity = 1;
}

function GetAIResponse(website, name, ASIN, token)
{
    const data = { website: website, name: name, asin: ASIN, token: token};

    fetch("http://localhost:5000/getAIResponse", {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    mode: 'cors',
    body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        try{
            var cons = data.Cons;
            var pros = data.Pros
            var oneline = data.One_Line;

            document.getElementById("oneline-summay").innerHTML = oneline
            console.log(pros)
            const ul = document.getElementById("pros-ul");
            pros.forEach(function(item) {
                const li = document.createElement("li");
                li.innerText = item;
                ul.appendChild(li);
            });

            const cul = document.getElementById("cons-ul");
            cons.forEach(function(item) {
                const li = document.createElement("li");
                li.innerText = item;
                cul.appendChild(li);
            });
        }catch(err){
            console.log("Error")
        }

        var element = document.getElementById("opaci");
        element.style.opacity = 1;
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        err()
    });
}


function Getredits(token)
{
    const data = {token: token};

    fetch("http://api.bezly.xyz/getCredits", {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    mode: 'cors',
    body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        err()
    });
}

function getASIN(url) {
    const regex = /\/([A-Z0-9]{10})/;
    const match = url.match(regex);
    if (match) {
      return match[1];
    }
    return null;
  }
