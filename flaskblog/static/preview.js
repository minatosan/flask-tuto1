$(document).ready(function(){
    $(function(){
      function readURL(input){
        if(input.files && input.files[0]){
          // FileReaderクラスを呼び出す
          var reader =new FileReader();
          // 読み込みが成功してからの処理
          reader.onload=function(e){
            // preview_imgに画像を差し替え
            $("#preview_img").attr("src",e.target.result);
          }
          reader.readAsDataURL(input.files[0]);
          }
        }
        $(".avatar_field").change(function(){
          // file-fieldが変化した時はreadURLメソッドを呼び出す
          readURL(this);
        });
    });
     
 });