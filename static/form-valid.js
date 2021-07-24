const name = document.getElementById('username')
const password = document.getElementById('password')
const form = document.getElementById('mainform')
const second_password = document.getElementById("secure_pass")


form.addEventListener('submit', (e) => {
  let messages = []
  if (name.value === '' || name.value == null) {
    messages.push('Name is required \n')
  }

  if (password.value.length <= 6) {
    messages.push('Password must be longer than 6 characters \n')
  }
  
  if (password.value != second_password.value){
    
    messages.push("Password doesn't match. \n")
    
  }
  

  if (password.value.length >= 20) {
    messages.push('Password must be less than 20 characters \n')
  }

  if (password.value === 'password') {
    messages.push('Password cannot be password \n')
  }

  if (messages.length > 0) {
    e.preventDefault()
    let data = JSON.stringify(messages)
    
    fetch(`${window.origin}/communicate`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(messages),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
    location.reload()
  }
 
})


