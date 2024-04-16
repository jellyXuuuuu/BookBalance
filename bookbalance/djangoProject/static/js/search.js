$(function(){
    $('#top_search').on('input',function(){
        var val = $(this).val()
        if(!val){
            $("#search_tips_con").html('')
            $("#search_tips_con").hide();
            return false;
        }
        $.ajax({
            url:'/goods/searchJson/?q='+val, success(res){
                if(res.code === 200){
                    $("#search_tips_con").show();
                    var htmlStr = '';
                    for(var i=0;i<res.data.length;i++){
                        htmlStr += '<li><a href="/goods/detail/'+res.data[i].id+'">'+ res.data[i].name+'</a></li>'
                    }
                    if(!htmlStr){
                        htmlStr = '<li><a href="javascript:;">没有搜索到内容</a></li>'
                    }
                    $("#search_tips_con").html(htmlStr);
                }
            }
        })
    })
})
