$(document).ready(function(){

  //検索結果
  var searchlist=$(".search_result");
  //HTML作成関数
  function appendHTML(data){
    var HTML=`
    <ul class="list-group mb-5">
      <li class="list-group-item">${data}</li>
    </ul>
    `
    searchlist.append(HTML);
  }
  //フォームに入力すると発火
  $(".search_field").on("keyup",function(){
    //フォームの値を取得
    var keys = $(".search_field").val();
   $.ajax({
     type: 'POST',
     url: '/user/result/',
     data: JSON.stringify({keyword: keys}),
     dataType: 'json',
     contentType: "application/json"
   })
   .done(function(data){
    searchlist.empty();
    if(data.length !== 0){
      data.forEach(function(data){
        appendHTML(data)
      })
    }
  }).fail(function(){
    alert("検索に失敗しました");
  })
  })
 
   
});