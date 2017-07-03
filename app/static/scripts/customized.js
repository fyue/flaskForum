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
			var url,
			    $middle = $(this),
			    $firstEle = $middle.children("span:first");
			if ($firstEle.is(":visible")){
				url = $middle.children("span:eq(2)").text();
			}else{
				url = $middle.children("span:eq(3)").text();
			}
			$.ajax({
				type: "GET",
				url: url,
				dataType: "json",
				success: function(data){
					if (data["thumbCounts"] !== undefined){ /*avoid quick click problem*/
						var thumbCount = data["thumbCounts"] + "人赞同";
						$middle.next().empty().text(thumbCount);
						/*exchange thumb and cancelthumb*/
						if ($firstEle.is(":visible")){
							$firstEle.hide();
							$firstEle.next().show();
						}else{
							$firstEle.show();
							$firstEle.next().hide();
						}
					}
				}
			})
			
			/*
			$.getJSON($(this).children("span.thumbs_hidden_url").text(), function(data){
				var thumbCount = data["thumbs"] + "个赞";
				$middle.children("span.thumbs_oprand").empty().text(thumbCount);
			});*/
		})
	})
})
