var CM = (function () {
    var priv = {},
        publ = {};
        
    priv.data = {
        usd: {
            start: 1000,
            end: 1500,
            buy: [{
                rate: 26,
                sum: 100
            },{
                rate: 26.5,
                sum: 100
            },{
                rate: 27,
                sum: 200
            }],
            sell: [{
                rate: 28,
                sum: 100
            }]
        },
        eur: {
            start: 1000,
            end: 1500,
            buy: [{
                rate: 28,
                sum: 100
            }],
            sell: [{
                rate: 26,
                sum: 100
            },{
                rate: 26.5,
                sum: 100
            },{
                rate: 27,
                sum: 200
            }]
        },
        rur: {
            start: 1000,
            end: 1500,
            buy: [],
            sell: []
        }
    };
    
    
    priv.drawOpLine = function (rate, sum) {
        var result;
            
        result =  '<tr class="row">' +
                  ' <td class="col-md-4">'+ rate +'</td>' +
                  ' <td class="col-md-4">'+ sum +'</td>' +
                  ' <td class="col-md-4">'+ sum * rate +'</td>' +
                  '</tr>';
                  
        return result;
    };
    
    priv.drawCurrencyData = function (name, params) {
        var name = name,
            start = params.start,
            end = params.end,
            buyList = params.buy,
            sellList = params.sell,
            result = "";
         
         result = '<div class="cur_data row"><div class="col-md-1"></div>' +
                  '<div class="currname col-md-1">' + name + '</div>' +
                  '<div class="start_balance col-md-1">' + start + '</div>' + 
                  '<div class="buyColumns col-md-3"><table class="table">';
                  
         buyList.forEach(function (item, i, arr) {
             result += priv.drawOpLine(item.rate, item.sum);
         });

         result +='</table></div><div class="sellColumns col-md-3"><table class="table">';
         
         sellList.forEach(function (item, i, arr) {
             result += priv.drawOpLine(item.rate, item.sum);
         });
         
         result +='</table></div><div class="col-md-1 end_balance">' + end + '</div></div>';
                  
                  
         return result;   
    }
    
    priv.updateHeights = function() {
        $(".cur_data").each(function(ind, item) {
            var blockHeight = $(item).height(),
                padding = blockHeight*0.4;
            if(blockHeight > 22) {
                $(".currname, .start_balance, .end_balance", item).height(blockHeight);
                $(".currname, .start_balance, .end_balance", item).css("padding-top", padding);
            }  
        });
    }
            
    publ.drawAllData = function () {
        var result = "",
            usdData = priv.data.usd,
            eurData = priv.data.eur,
            rurData = priv.data.rur;
        
        result += priv.drawCurrencyData("USD", usdData);
        result += priv.drawCurrencyData("EUR", eurData);
        result += priv.drawCurrencyData("RUR", rurData);
        
        $(".main").html(result);
        priv.updateHeights();
    }  
    
    return publ;
})();

$(document).ready(CM.drawAllData);