$(function(){
	$("div#verifyImg a").click(function(){
		$.getJSON("/api/v1.0/verifyName", function(data){
			$("div#verifyImg img").remove();
			var html = "";
			html = '<img src="/static/verifyCode/' + data["verifyName"] +
				    '" />';
			$("div#verifyImg a").before(html);
		})
	})
})