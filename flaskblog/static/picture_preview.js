$(document).ready(function(){
  $(function(){
    function readURL(input){
      if(input.files && input.files[0]){
        var reader =new FileReader();
        $(".preview-img").append("画像のプレビューです")
        reader.onload=function(e){
          $(".preview-img").append(`<img class="preview" width="200px" height="200px">`);
          $(".preview").attr("src",e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
        }
      }
      $(".picture_field").change(function(){
        readURL(this);
      });
  });
   
});