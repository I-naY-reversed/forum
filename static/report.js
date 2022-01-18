function reportUser(id) {
  fetch(`/report-user/` + id).then((response) => {  response.json().then((data) => {
    if(data.length){
      snb("Reported User Successfully");
      return;
    }
    snb("User Report Failed");
  })
  })
}

function reportPost(id) {
  fetch(`/report-post/` + id).then((response) => { response.json().then((data) => {
    if(data.length){
      snb("Reported Post Successfully");
      return;
    }
    snb("Post Report Failed");
  })
  })
}