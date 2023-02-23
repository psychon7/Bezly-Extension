window.onload = function(){
    console.log("Windows Loadeds")
    chrome.storage.sync.set({'foo': 'hello', 'bar': 'hi'}, function() {
        console.log('Settings saved');
    });

    document.getElementById("review-button").addEventListener('click', function(){
        window.location.replace("./main.html")
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

    var element = document.getElementById("opaci");
    element.style.opacity = 1;
}
