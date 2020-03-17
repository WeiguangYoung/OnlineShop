var BASE_URL = baseUrl
function main(data) {
    var cart = {};
    cart.data = {
        html: function () {
            //遍历数据
            var HTML = '';
            for (var i = 0; i < data.length; i++) {
                HTML += ' <div class="imfor">'
                HTML += '           <div class="check">'
                HTML += '                <div class="Each">'
                HTML += '                     <input type="checkbox" checked name="" value="' + data[i].id + '">'
                HTML += '                 </div>'
                HTML += '           </div>'
                HTML += '            <div class="pudc">'
                HTML += '               <div class="pudc_information" id="pudcId1">'
                HTML += '                    <img src="../static/media/' + data[i].default_image_url +
                    '" class="lf"  style="width: 70px"/' +
                    '>'
                HTML += '                   <input type="hidden" name="" value="">'
                HTML += '                    <span class="des lf">'
                HTML += data[i].name
                HTML += '                       <input type="hidden" name="" value="">'
                HTML += '                   </span>'
                var skuName = data[i].sku_sale_attr_name
                for (var j = 0; j < skuName.length; j++) {
                    HTML += '<p class="col lf"><span>' + skuName[j] + '：</span><span class="color_des">' + data[i].sku_sale_attr_val[j] + '</span></p>'
                }
                HTML += '               </div>'
                HTML += '           </div>'
                HTML += '           <div class="pices">'
                HTML += '              <p class="pices_des">阿甲专享价</p>'
                HTML += '               <p class="pices_information"><b>￥</b><span class="pices_price">' + data[i].price +
                    '</span></p>'
                HTML += '           </div>'
                HTML +=
                    '           <div class="num"><span class="reduc">&nbsp;-&nbsp;</span><input class="num1207" data-id="' +
                    data[i].id + '" readonly type="text"'
                HTML += '                  value="' + data[i].count +
                    '" /><span class="add">&nbsp;+&nbsp;</span></div>'
                HTML += '           <div class="totle">'
                HTML +=
                    '                                                                     <span>￥</span>'
                HTML += '           <span data-id="' + data[i].id + '" class="totle_information">' + data[i].count * data[i].price +
                    '</span>'
                HTML += '       </div>'
                HTML += '      <div class="del">'
                HTML += ' <a href="javascript:;" data-id="' + data[i].id + '" class="del_d">删除</a>'
                HTML += ' </div>'
                HTML += '</div>'
            }
            return HTML;
        },
        sumPrice: function () {
            var _s = 0;
            $(".totle_information").each(function (i, e) {
                _s += Number($(e).text());
            })
            $(".susumOne,.susum").html(_s);
        },
        sumNum: function () {
            var _n = $(".Each input:checkbox:checked").length;
            $(".totalOne,.total").html(_n);
        },
        checkAll: function () {
            var _blnAllCheck = false;
            $(".Each input[type='checkbox']").each(function (i, e) {
                if ($(e).prop("checked")) {
                    _blnAllCheck = true
                } else {
                    _blnAllCheck = false;
                }
            })
            return _blnAllCheck;
        },
        delItem: function (index) {
            $(".Each input[type='checkbox']").each(function (i, e) {
                if ($(e).val() == index) {
                    var username = window.localStorage.dashop_user;
                    if (username){
                        $.ajax({
                        url: BASE_URL+'/v1/carts/' + username,
                        type: "DELETE",
                        beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
                        dataType: "json",
                        data: JSON.stringify({'sku_id': index}),
                        success: function (result) {
                            window.localStorage.setItem('dashop_count',result.data.length)
                            $('.my_cart_count').html(result.data.length)
                            if(result.data.length == 0){
                                    $("#go-buy").css("background","gray")
                                    $("#go-buy").attr("disabled",true)
                            }
                        }
                    });
                    }else {
                        var result = '';
                        for(var j=0;j<data.length;j++){
                           if (data[j].id == index){
                               data.splice(j,1);
                               result = data;
                               console.log(data);
                           }
                        }
                        window.localStorage.setItem('cart',JSON.stringify(result))
                    }
                    $(".imfor").each(function (i2, e2) {
                        if (i == i2) {
                            $(e2).remove();
                        }
                    })
                }
            })
        }

    }

    $(".imfor_top").after(cart.data.html());
    cart.data.sumNum();
    cart.data.sumPrice();
    //数量增加和减少事件
    $(".reduc").each(function (i, e) {
        $(e).on("click", function () {
            //alert(i)
            var _v = $(this).next();
            var _v2 = Number(_v.val());
            if (_v2 > 1) {
                _v2--;
                _v.val(_v2);
                if ($(this).parent().parent().children('.check').children('.Each').children().prop('checked')){
                    var _price = parseInt($(this).parent().prev().children('.pices_information').children('.pices_price').text());
                    var _totalprice = parseInt($(".susumOne").text());
                    console.log(_price)
                    console.log(_totalprice)
                    _totalprice -= _price;
                    $(".susumOne,.susum").text(_totalprice)
                }
            }
            var _id = _v.data("id");
            $(".totle_information").each(function (i2, e2) {
                if (_id == $(e2).data("id")) {
                    var _p = data[i2].price;
                    $(e2).html(_p * _v2)
                }
            })
            var username = window.localStorage.dashop_user;
            var sku_id = $(this).parent().parent().children('.check').children('.Each').children().val()
            $.ajax({
                url : BASE_URL+'/v1/carts/'+username,
                type : "PUT",
                beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
                dataType: "json",
                data : JSON.stringify({'sku_id':sku_id,'count':_v2,'state':'del'}) ,
                success : function(result) {
                console.log(result.msg);
                }
            });

            })
        })
    $(".add").each(function (i, e) {
        $(e).on("click", function () {
            var _v = $(this).prev();
            var _v2 = Number(_v.val());
            var _id = _v.data("id");
            var username = window.localStorage.dashop_user;
            var sku_id = $(this).parent().parent().children('.check').children('.Each').children().val()
            var nodelabel = $(this)
            $.ajax({
                url :  BASE_URL+'/v1/carts/'+username,
                type : "PUT",
                dataType: "json",
                beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
                data :JSON.stringify({'sku_id':sku_id,'state':'add'}) ,
                success : function(result) {
                    console.log(result)
                    if (result.code == 200){
                        console.log(result.code)
                        if (_v2 < 10) {
                            _v2++;
                            _v.val(_v2)
                            if (nodelabel.parent().parent().children('.check').children('.Each').children().prop('checked')){
                                var _price = parseInt(nodelabel.parent().prev().children('.pices_information').children('.pices_price').text());
                                var _totalprice = parseInt($(".susumOne").text());
                               _totalprice += _price;
                               console.log(_price)
                                console.log(_totalprice)
                           $(".susumOne,.susum").text(_totalprice)
                            }
                        }
                        $(".totle_information").each(function (i2, e2) {
                            if (_id == $(e2).data("id")) {
                                var _p = data[i2].price;
                                $(e2).html(_p * _v2)
                                $(".totalPrices color susum")
                            }
                        });
                    }else if (result.code==30103){
                        alert("购买数量超过过库存")
                    }
                }
            });

        })
    })
    //每个单选按钮事件
    $('.Each>input').click(function () {
        var username = window.localStorage.dashop_user;
        var sku_id = $(this).val()
        console.log(sku_id)
        if ($(this).prop('checked')) {
            var amou = parseInt($('.total').text());
            amou++;
            $('.total').text(amou);
            $('.totalOne').text(amou);
            var newamo = parseInt($('.susum').text()) + parseInt($(this).parent().parent().siblings('.totle').children('.totle_information').text());
            $('.susum').text(newamo);
            $('.susumOne').text(newamo);
            console.log($(".Each input[type=checkbox]:not(:checked)"))
            if($(".Each input[type=checkbox]:checked").length > 0){
                $("#go-buy").css("background","#997679")
                $("#go-buy").attr("disabled",false)
                
            }
            if($(".Each input[type=checkbox]:not(:checked)").length > 0){
                $("input[name=allcheck]").attr("checked",false)
            }
            if($(".Each input[type=checkbox]:not(:checked)").length == 0){
                $("input[name=allcheck]").prop("checked",true)
            }   
            $.ajax({
                url :  BASE_URL+'/v1/carts/'+username,
                type : "PUT",
                dataType: "json",
                beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
                data : JSON.stringify({'sku_id':sku_id,'state':'select'}) ,
                success : function(result) {
                }
            });
        } else {
            var amou = parseInt($('.total').text());
            amou--;
            $('.total').text(amou);
            $('.totalOne').text(amou);
            var newamo = parseInt($('.susum').text()) - parseInt($(this).parent().parent().siblings('.totle').children('.totle_information').text());
            $('.susum').text(newamo);
            $('.susumOne').text(newamo);
            if($(".Each input[type=checkbox]:checked").length == 0){
                $("#go-buy").css("background","gray")
                $("#go-buy").attr("disabled",true)
            }
            if($(".Each input[type=checkbox]:not(:checked)").length > 0){
                $("input[name=allcheck]").attr("checked",false)
            }
            if($(".Each input[type=checkbox]:not(:checked)").length == 0){
                $("input[name=allcheck]").prop("checked",true)
            }           
            $.ajax({
                url :  BASE_URL+'/v1/carts/'+username,
                type : "PUT",
                dataType: "json",
                beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
                data : JSON.stringify({'sku_id':sku_id,'state':'unselect'}) ,
                success : function(result) {
                console.log(result.msg);

                }
            });
        }
        
    })
    //删除事件
    $(".del_d").each(function (i, e) {
        $(this).on("click", function () {
            _index = $(this).data("id");
            $(".modal").show();
        })
    })
    $(".modal_dialog .yes").on("click", function () {
        cart.data.delItem(_index);
        $(".modal").hide();
        cart.data.sumPrice();
        if($("div[class=imfor]").length == 0){
            $("#go-buy").css("background","gray")
            $("#go-buy").attr("disabled",true)
            $("input[name=allcheck]").attr("checked",false)
        }
        if ($(".total").text() == "0") {
            $(".none").show();
        }
    })
    $(".modal_dialog .no").on("click", function () {
        $(".modal").hide();
    })
    if (!$(".imfor")) {
        $('#section').hide();
        $('.none').show();
    }
    var cart_list = $('.Each>input')
    var sku_list = []
    for (var i=0;i<cart_list.length;i++){
        sku_list.push($('.Each>input')[i].value)
    }
    $("#allcheck,#allcheck2").on("click", function () {
    var username = window.localStorage.dashop_user;
    var sku_id = sku_list;
    if ($(this).prop("checked")) {
        $(".Each input[type='checkbox']").prop("checked", true);
        $("#allcheck,#allcheck2").prop("checked", true)
        cart.data.sumNum();
        cart.data.sumPrice();

        $.ajax({
            url : BASE_URL+'/v1/carts/'+username,
            type : "PUT",
            dataType: "json",
            beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
            data : JSON.stringify({'sku_id':sku_id,'state':'selectall'}) ,
            success : function(result) {
            console.log(result.msg);
            }
        });

    } else {
        $(".Each input[type='checkbox']").prop("checked", false);
        $("#allcheck,#allcheck2").prop("checked", false)
        $(".susumOne,.susum").html(0);
        $(".totalOne,.total").html(0);
        $.ajax({
            url : BASE_URL+'/v1/carts/'+username,
            type : "PUT",
            dataType: "json",
            beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
            data : JSON.stringify({'sku_id':sku_id,'state':'unselectall'}) ,
            success : function(result) {
            console.log(result.msg);
            if (result.dada.length == 0){
                $("#go-buy").css("background","gray")
                $("#go-buy").attr("disabled",true)                
            }
            }
        });
    }

})
}


$(function () {
     var username = window.localStorage.dashop_user;
     if (username) {
         $.ajax({
             type: "get",
             url: BASE_URL+'/v1/carts/'+username,
             datatype: JSON,
             beforeSend:function (request) {
                 request.setRequestHeader('authorization',window.localStorage.getItem('dashop_token'))
             },
             success: function (reponse) {
                 result = JSON.stringify(reponse)
                 results = JSON.parse(result)
                 if (results.code == 200) {
                     var data = results.data;
                     console.log(data)
                     if (data.length == 0){
                         $("#go-buy").css("background","gray")
                         $("#go-buy").attr("disabled",true)
                     }
                     main(data)
                 } else {
                     alert(results.error)
                 }
             },
             error: function (err) {
                 console.log(err);
             },
         })
     }else {
         var data = JSON.parse(window.localStorage.getItem('cart'))
         console.log(data)
         main(data)
     }
})


$("#go-buy").click(function () {
    var username = window.localStorage.dashop_user;
    if (username == null){
        alert("请登录后结算")
        window.location.href = "login.html"
    }else{
        var arrOutput = [];
	$(".Each input:checkbox:checked").each(function (i, e) {
		$('.num1207').each(function (i2, e2) {
			if ($(e).val() == $(e2).data("id")) {
				var _obj = {}
				_obj.id = $(e2).data("id");
				_obj.num = $(e2).val()
				arrOutput.push(_obj)
			}
		})
    })
    window.location.href = "orderConfirm.html"
    }
    

})
