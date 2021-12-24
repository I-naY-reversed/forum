var counter = 0;
var load_obj = document.getElementById("loadmore")

function loadNext() {
  fetch(`/loadmore?ctr=${counter}`).then((response) => {
    response.json().then((data) => {
      if (!data.length) {
        load_obj.innerText = "Thats all of the posts so far...";
        return;
      }

      let tmpl = document.querySelector('#post_temp').content.cloneNode(true);
      let post = data[0];
      tmpl.querySelector("#t_title").innerText = post[0];
      tmpl.querySelector("#t_user").innerText = post[1];
      tmpl.querySelector("#t_user").href = '/profile/' + post[1];
      tmpl.querySelector("#t_ago").innerText = post[2];
      tmpl.querySelector("#t_content").innerText = post[3];
      tmpl.querySelector("#t_coms").innerText = post[4] + ' comments ';
      tmpl.querySelector("#t_carda").href = '/thread/' + post[5];
      counter += 1;
      document.getElementById("dynload").appendChild(tmpl);
    })
  })
}

var intersectionObserver = new IntersectionObserver(entries => {
  if (entries[0].intersectionRatio <= 0) {
    return;
  }
  loadNext();
})

intersectionObserver.observe(load_obj);