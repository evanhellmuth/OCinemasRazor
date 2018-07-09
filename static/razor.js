jQuery(function($){
		$('.menu-btn, .overlay').click(function(){
			$('.navbar').toggleClass('expand')
			$('.divider-line').toggle()
			$('.overlay').toggle()
		})
	})

$(window).resize(function() {
	if ($(window).width() >= 690) {
		$('.navbar').removeClass('expand')
		$('.divider-line').hide()
		$('.overlay').hide()
	}
})