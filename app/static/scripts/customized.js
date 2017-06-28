$(function(){
	$("div#verifyImg a").click(function(){
		$.getJSON("/api/v1.0/verifyName", function(data){
			source = "/static/verifyCode/" + data["verifyName"];
			$("div#verifyImg img").removeAttr("src").attr("src", source);
		})
	})
})

$(function(){
	$("div.post-footer a.thumbs").each(function(){
		$(this).click(function(){
			var $middle = $(this)
			$.ajax({
				type: "GET",
				url: $middle.children("span.thumbs_hidden_url").text(),
				dataType: "json",
				success: function(data){
					var thumbCount = data["thumbs"] + "个赞";
					$middle.children("span.thumbs_count").empty().text(thumbCount);
				}
			})
			
			/*
			$.getJSON($(this).children("span.thumbs_hidden_url").text(), function(data){
				var thumbCount = data["thumbs"] + "个赞";
				$middle.children("span.thumbs_count").empty().text(thumbCount);
			});*/
		})
	})
})
