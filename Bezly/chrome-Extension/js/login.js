document.addEventListener("DOMContentLoaded", function() {
    var element = document.getElementById("daccs");
    element.addEventListener("click", function() {
      // Do something when the element is clicked
      window.location.replace("./register.html")
    });

    var login = document.getElementById("login-btr");
    login.addEventListener("click", function() {
        var suc = () => Swal.fire({
            icon: 'success',
            title: 'Success',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
        
        var err = () => Swal.fire({
            icon: 'error',
            title: 'Errors',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
          });
      // Do something when the element is clicked
      var email = document.getElementById("email-input").value
      var password = document.getElementById("password-input").value

      if(email != "" && password != ""){
        LoginWithEmailAndPassword(email, password)
      }else{
        err()
      }
    });
});

function LoginWithEmailAndPassword(email, password)
{
    var suc = () => Swal.fire({
        icon: 'success',
        title: 'Success',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000
    });
    
    var err = () => Swal.fire({
        icon: 'error',
        title: 'Errors',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000
      });
    const data = { email: email, password: password};
    fetch("http://api.bezly.xyz/login", {
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
        chrome.storage.sync.set({'auth': data.idToken}, function() {
            console.log('Settings saved');
        });
        suc();
        window.location.replace("./index.html")
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        err()
    });
}