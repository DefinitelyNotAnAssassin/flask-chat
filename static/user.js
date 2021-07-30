function hello (e) {
 
let messages = {
  name:e.parentNode.parentNode.id,
  identifier: e.parentNode.id
}



let confirm_delete = confirm("Delete message? ")




if (confirm_delete == true){
e.parentNode.parentNode.parentNode.parentNode.removeChild(e.parentNode.parentNode.parentNode)
  
  
  fetch(`${window.origin}/delete`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(messages),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  
}


}

function send_name(){
  let name = document.getElementById("name")
  let username = []
  username.push(name.innerText)
  
  fetch(`${window.origin}/add_friend`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(username),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  location.reload() 
}