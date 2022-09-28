window.addEventListener('contextmenu', (event) => {
    console.log('Target:  ');
    console.log(event.target);
    console.log('Class:  ');
    let myclass=event.target.getAttribute("class");
    console.log(myclass);
    //See if class contains modal
    if (myclass==null) {
       containsmodal=false
    }
    else if (myclass.search('modal')!=null) {
       containsmodal=true;
    }
    else containsmodal=false;


    console.log('Parent:  ');
    console.log(event.target.parentElement);
    mytarget=event.target.getAttribute("data-id");

    if (mytarget=="layer0-selectbox" || containsmodal ) {
        console.log(mytarget);
        event.preventDefault();
    }
    else {
        console.log('Not in Cyto');
        //do nothing
     }
    })

