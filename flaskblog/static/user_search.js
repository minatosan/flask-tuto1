$(document).ready(function(){

  //検索結果
  var searchlist=$(".search_result");
  //HTML作成関数
  function appendHTML(data){
    var HTML=`
    <ul class="list-group mb-5">
      <li class="list-group-item">${data[0]}</li>
      <li class="list-group-item"><a href='/user/show/${data[1]}'>プロフィールを確認</a></li>
    </ul>
    `
    searchlist.append(HTML);
  }
  //フォームに入力すると発火
  $(".search_field").on("keyup",function(){
    //フォームの値を取得
    var keys = $(".search_field").val();
  // ajax通信を行う
   $.ajax({
     type: 'POST',
     url: '/user/result/',
     data: JSON.stringify({keyword: keys}),
     dataType: 'json',
     contentType: "application/json"
   })
   .done(function(data){
    // 一度、サーチリストを空にする(前回の検索結果の消去)
    searchlist.empty();
    if(data.length !== 0){
      // each文を回して検索結果を表示させていく
      data.forEach(function(data){
        appendHTML(data)
      })
    }
  }).fail(function(){
    alert("該当のユーザーが見つかりませんでした");
  })
  })
});