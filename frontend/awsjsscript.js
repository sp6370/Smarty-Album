function getPhoto()
{
  var apigClient = apigClientFactory.newClient({
                     apiKey: "N2COeKa5TFEmsEMA7jA63v5KWjFFSsA61v930lg8"
        });
    var user_message = document.getElementById('note-textarea').value;
    var body = {};
    var params = {q : user_message};
    var additionalParams = {headers: {
    'Content-Type':"application/json"
  }};

    apigClient.searchGet(params, body , additionalParams).then(function(result){
        rdata  = result.data
        length_of_response = rdata.length;
        if(length_of_response == 0)
        {
          document.getElementById("custom_message").innerHTML = "Try with another keyword, no images found."
          document.getElementById("custom_message").style.display = "block";
        }

        rdata.forEach( function(obj) {
            var img = new Image();
            img.src = "https://photobalti.s3.us-east-1.amazonaws.com/"+obj;
            img.setAttribute("class", "banner-img w-1/3 h-1/4 py-8");
            img.setAttribute("alt", "effy");
            document.getElementById("custom_message").innerHTML = "Photos found:-"
            document.getElementById("img-container").appendChild(img);
            document.getElementById("custom_message").style.display = "block";

          });
      }).catch( function(result){

      });
}

function convertImgBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
      if ((encoded.length % 4) > 0) {
        encoded += '='.repeat(4 - (encoded.length % 4));
      }
      resolve(encoded);
    };
    reader.onerror = error => reject(error);
  });
}

function imgSuccess() {
  alert("Image Uploaded Successfully");
}

function imgFail() {
  alert("Image Not Uploaded. Try Again!");
}

function submitPhoto()
{
   var img_file = document.getElementById('file_path').files[0];
   var mlabels = document.getElementById('clabel').value;
   
   var base64_image = convertImgBase64(img_file).then(
     promise_data => {
     var apigClient = apigClientFactory.newClient({
                       apiKey: "N2COeKa5TFEmsEMA7jA63v5KWjFFSsA61v930lg8"
          });
     
    
     var request_body = promise_data;
     var params = {"key" : img_file.name, "bucket" : "photobalti", "Content-Type" : img_file.type, "x-amz-meta-CustomLabels": mlabels};
     
     console.log(params)

     var additionalParams = {};

     apigClient.uploadBucketKeyPut(params, request_body , additionalParams).then(function(res){
       if (res.status == 200)
       {  
         imgSuccess();
       }
       else{
        imgFail();
       }
     })
   });

}
