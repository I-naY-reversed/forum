function ignoreerror()
{
  return true
}
window.onerror=ignoreerror();

function inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

function strip(html){
  let doc = new DOMParser().parseFromString(html, 'text/html');
  return doc.body.textContent || "";
}

function OnInput() {
  this.style.height = "auto";
  this.style.height = (this.scrollHeight) + "px";
}

function replaceAtMentionsWithLinks (text) {
  return text.replace(/@([a-z\d_]+)/ig, '<a href="https://forum.eniac1.repl.co/profile/$1">@$1</a>'); 
}

function md(that) {
  that.innerText = replaceAtMentionsWithLinks(that.innerText);
  let a = DOMPurify.sanitize(marked.parse(that.innerText));
  if (a == ""){
    a = "Content removed due to possibly malicious content.";
  }
  that.innerHTML = a;
  }

function init() {
  if (inIframe()) {
    setTimeout(function() { snb('You cannot use some of the features of this forum in an iframe, please open it in a new tab.'); }, 1);
  }
  let loader = document.getElementById("loader");
  loader.style.display = "none";
  loader.remove();
  document.body.style.display = "flex";
  let x = document.getElementsByClassName("content");
  var i;
  for (i = 0; i < x.length; i++) {
    x[i].innerHTML.replace(/</g,'&lt;');
    md(x[i]);
  }

  const tx = document.getElementsByTagName("textarea");
  for (let i = 0; i < tx.length; i++) {
    try{
    tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:hidden;");
    tx[i].addEventListener("input", OnInput, false);
    }
    catch(e){
      console.log(e);
    }
  }
  hText();
  try{
    MathJax.typeset();
  }
  catch(e){
    console.log('no mathjax');
  }
}

function replyTo(text, comment_content) {
  var content = document.getElementById("content");
  content.value = '<div class="reply"><a href="' + text + '"><q> ' + strip(DOMPurify.sanitize(comment_content)) + '</q></a></div>' + content.value;
}


function partybtnclick() {
  party.confetti(document.getElementById("partybtn"))
}

window.onload = function() {
  init();
  try {
    document.getElementById("partybtn").addEventListener("click", partybtnclick);
  }
  catch (e){
    console.log(e);
  }
}

function snb(text) {
  var x = document.getElementById("sb");
  x.innerText = text;
  x.className = "show";

  setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
}

function hText(){
  if (getCookie('greeted') == ''){
    document.getElementById('modial').style.display = 'block';
    window.onclick = function(event) {
    if (event.target == document.getElementById('modial')) {
        document.getElementById('modial').style.display = "none";
      }
    }
    setCookie('greeted', 'true', 30);
  }
}

function closeMod(){
  document.getElementById('modial').style.display = 'none';
}

function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}