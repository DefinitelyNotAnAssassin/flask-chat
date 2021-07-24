function hello (e) {
 
let messages = {
  name:e.parentNode.parentNode.id,
  date: e.parentNode.id,
  id: e.parentNode.parentNode.parentNode.id 
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