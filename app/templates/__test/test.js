//by Dima

//var Changer = (function(){
//
//    var pub = {},
//        pr = {};
//
//    pr.currency = '';
//    pr.direction = '';
//
//    pr.sum = 0;
//    pr.course = 0;
//    pr.result = 0;
//
//    pr.balances = {
//        balUAH: 0,
//        balUSD: 0,
//        balEUR: 0,
//        balRUB: 0
//    };
//
//    pr.isBuy = function() {
//        return pr.directon === 'BUY';
//    };
//
//    pr.isOperationConditionsSet = function() {
//        return (pr.currency && pr.directon) || false;
//    };
//
//
//    pr.updateBalances = function() {
//        pr.balances.balUAH = parseFloat($('#balance_UAH').text());
//        pr.balances.balUSD = parseFloat($('#balance_USD').text());
//        pr.balances.balEUR = parseFloat($('#balance_EUR').text());
//        pr.balances.balRUB = parseFloat($('#balance_RUB').text());
//    };
//
//    pr.updateNumbers = function() {
//
//        var sum = 0,
//            course = 0;
//
//        pr.sum = parseFloat($('#sum').val()) || 0;
//        pr.course = parseFloat($('#course').val().replace(/\,/i, '.')) || 0;
//        pr.result = pr.course * pr.sum;
//
//        $('#result').val(pr.result.toFixed(2));
//    };
//
//
//    pr.updateCurrency = function(currency) {
//        //pr.currency = $('#currency label.active > input').val();
//        pr.currency = currency;
//    };
//
//    pr.updateDirection = function(directon) {
//        //pr.directon = $('#oper label.active > input').val();
//        pr.directon = directon;
//    };
//
//
//    pr.isOperationSumCorrect = function() {
//        var sum = pr.sum,
//            balance = 0;
//
//        if (pr.result === 0){
//            return false;
//        }
//
//        if(pr.isBuy()) {
//            balance = pr.balances.balUAH;
//            sum = pr.result;
//        } else {
//            switch (pr.currency) {
//                case 'USD':
//                    balance = pr.balances.balUSD;
//                    break;
//                case 'EUR':
//                    balance = pr.balances.balEUR;
//                    break;
//                case 'RUB':
//                    balance = pr.balances.balRUB;
//                    break;
//            }
//        }
//
//        return ((balance - sum) >= 0);
//    };
//
//    pr.checkIfOperationCorrect = function() {
//        var isCorrect = true;
//
//        pr.updateNumbers();
//
//        isCorrect = pr.isOperationConditionsSet();
//
//        if(isCorrect) {
//            isCorrect = pr.isOperationSumCorrect();
//        }
//
//        if(isCorrect) {
//            pub.active_button();
//        } else {
//            pub.deactive_button();
//        }
//    };
//
//
//    pub.active_button = function() {$('button[data-target=".bs-example-modal-sm"]').prop('disabled', false)};
//    pub.deactive_button = function() {$('button[data-target=".bs-example-modal-sm"]').prop('disabled', true)};
//
//    pub.setHandlers = function() {
//
//        pr.updateBalances();
//
//        $('#sum').keyup(pr.checkIfOperationCorrect);
//
//        $('#course').keyup(pr.checkIfOperationCorrect);
//
//
//        $('#oper label').click(function(evData){
//            var oper = evData.currentTarget.attributes['data-op'].value;
//            pr.updateDirection(oper);
//            pr.checkIfOperationCorrect();
//        });
//
//        $('#currency label').click(function(evData){
//            var cur = evData.currentTarget.attributes['data-cur'].value;
//            pr.updateCurrency(cur);
//            pr.checkIfOperationCorrect();
//        });
//    }
//
//    return pub;
//
//})();
//$(document).ready(Changer.setHandlers());

//by Me

////////////////////////
//$(document).ready(function(){
//        $('#sum').keyup(function(){
//            var Result = $('#course').val() * $('#sum').val();
//            $('#result').val(Result.toFixed(2));
//            //
//            checkBalance();
//            //
//        });
//        $('#course').keyup(function(){
//            var Result = $('#course').val() * $('#sum').val();
//            $('#result').val(Result.toFixed(2));
//            //
//            checkBalance();
//            //
//        });
//        $('#course').keypress(function() {
//            var value = $(this).val();
//            $(this).val(value.replace(/\,/i, '.'));
//        });
//
//
//        //Активация кнопки с условиями если;
//        var c1, c2, correctMoney;
//
//        $('#oper').click(function(){
//            c1=true;
//            checkBalance();
//        });
//        $('#currency label').click(function(){
//            c2=true;
//            checkBalance();
//        });
//
//        //Активация и деактивация кнопки;
//        active_button = function() {$('button[data-target=".bs-example-modal-sm"]').prop('disabled', false)}
//        deactive_button = function() {$('button[data-target=".bs-example-modal-sm"]').prop('disabled', true)}
//
//        //Основное условие;
//        checkAll = function(){
//            if (c1==c2==correctMoney) {
//                active_button();
//            } else {
//                deactive_button();
//            }
//        };
//
//        checkBalance = function() {
//            balUAH = parseFloat($('#balance_UAH').text());
//            balUSD = parseFloat($('#balance_USD').text());
//            balEUR = parseFloat($('#balance_EUR').text());
//            balRUB = parseFloat($('#balance_RUB').text());
//
//            sumCur = parseFloat($('#sum').val());
//            resUAH = parseFloat($('#result').val());
//
//            if ($('#oper label.active > input').val() == 'BUY') {
//                if ((balUAH - resUAH) >= 0) {
//                    correctMoney = true;
//                    checkAll();
//                } else {
//                    deactive_button();
//                };
//            };
//
//            if ($('#oper label.active > input').val() == 'SELL') {
//                switch ($('#currency label.active > input').val()) {
//                    case 'USD':
//                        if (balUSD >= sumCur) {
//                            correctMoney = true;
//                            checkAll();
//                        } else {
//                            deactive_button();
//                        };
//                        break;
//                    case 'EUR':
//                        if (balEUR >= sumCur) {
//                            correctMoney = true;
//                            checkAll();
//                        } else {
//                            deactive_button();
//                        };
//                        break;
//                    case 'RUB':
//                        if (balRUB >= sumCur) {
//                            correctMoney = true;
//                            checkAll();
//                        } else {
//                            deactive_button();
//                        };
//                        break;
//                };
//
//            };
//        };
//
//
//        //Преобразование таблицы во float с двумя запятыми;
//        for (var i= 0; i<$('#state_cash td').length; i++) {
//            var get_value = parseFloat($('#state_cash td')[i].innerText).toFixed(2);
//            $('#state_cash td')[i].innerText = get_value;
//        };
//
//        //Передача данных из form в модальное окно;
//        $('button[data-toggle="modal"]').click(function() {
//            $('#modal_sum').text($('#result').val());
//        });
//    });

////////////////////////

//by Me New
// var Inkass = (function() {
//
//     var pub = {},
//         pr = {};
//
//     pr.balances = {
//         UAH: 0,
//         USD: 0,
//         EUR: 0,
//         RUB: 0
//     };
//
//     pr.numbers = {
//         UAH: 0,
//         USD: 0,
//         EUR: 0,
//         RUB: 0
//     };
//
//     pr.direction = '';
//
//     //
//     pr.updateBalances = function() {
//         pr.balances.UAH = parseFloat($('#balance_UAH').text());
//         pr.balances.USD = parseFloat($('#balance_USD').text());
//         pr.balances.EUR = parseFloat($('#balance_EUR').text());
//         pr.balances.RUB = parseFloat($('#balance_RUB').text());
//     };
//
//     pr.updateNumbers = function() {
//         pr.numbers.UAH = parseFloat($("[name='UAH']").val()) || 0;
//         pr.numbers.USD = parseFloat($("[name='USD']").val()) || 0;
//         pr.numbers.EUR = parseFloat($("[name='EUR']").val()) || 0;
//         pr.numbers.RUB = parseFloat($("[name='RUB']").val()) || 0;
//     };
//
//     pr.updateDirection = function(direction) {
//         pr.direction = direction;
//     };
//
//     //
//     pr.isGIVE = function() {
//         if (pr.direction === 'GIVE') {
//             return true;
//         } else {
//             return false;
//         }
//     };
//
//     //
//     pr.checkBalance = function() {
//         pr.updateBalances();
//         pr.updateNumbers();
//
//         var isCorrect = true;
//
//         for (var i in pr.balances) {
//             if (pr.balances[i]-pr.numbers[i] < 0) {
//                 isCorrect = false;
//             };
//         };
//
//         return isCorrect;
//     };
//
//     //
//     pr.isIfConditionsCorrect = function() {
//         if (pr.isGIVE()) {
//             if (pr.direction && pr.checkBalance()) {
//                 pub.active_button();
//             } else {
//                 pub.deactive_button();
//             }
//         } else {
//             pub.active_button();
//         }
//     };
//
//
//     pub.active_button = function() {$('button[data-target=".bs-example-modal-sm"]').prop('disabled', false)};
//     pub.deactive_button = function() {$('button[data-target=".bs-example-modal-sm"]').prop('disabled', true)};
//
//     pub.setHandlers = function() {
//
//         $('#oper').click(function(evData){
//             var oper = evData.target.attributes['data-op'].value;
//             pr.updateDirection(oper);
//             pr.isIfConditionsCorrect();
//         })
//
//         $('.input-group input').keyup(function() {
//             pr.updateBalances();
//             pr.isIfConditionsCorrect();
//         })
//
//
//         //FROM OLD FILE
//         for (var i= 0; i<$('#state_cash td').length; i++) {
//             var get_value = parseFloat($('#state_cash td')[i].innerText).toFixed(2);
//             $('#state_cash td')[i].innerText = get_value;
//         };
//
//         $('button[data-target=".bs-example-modal-sm"]').click(function(){
//             $('#modal-uah').text(pr.numbers['UAH']);
//             $('#modal-usd').text(pr.numbers['USD']);
//             $('#modal-eur').text(pr.numbers['EUR']);
//             $('#modal-rub').text(pr.numbers['RUB']);
//         });
//
//     };
//
//     return pub;
// })();

// $(document).ready(Inkass.setHandlers());

//by Me Old


//(document).ready(function(){
//            for (var i= 0; i<$('#state_cash td').length; i++) {
//                var get_value = parseFloat($('#state_cash td')[i].innerText).toFixed(2);
//                $('#state_cash td')[i].innerText = get_value;
//            };
//
//            $('label.btn-success').click(function(){
//                $('button[data-target=".bs-example-modal-sm"]').prop('disabled', false);
//            });
//
//            $('button[data-target=".bs-example-modal-sm"]').click(function(){
//                $('#modal-uah').text($('input[name="UAH"]').val());
//                $('#modal-usd').text($('input[name="USD"]').val());
//                $('#modal-eur').text($('input[name="EUR"]').val());
//                $('#modal-rub').text($('input[name="RUB"]').val());
//            });
//        });

var AddUser = (function(){

    var pub = {};
    var pr = {};

    pr.changeState = function(cs){
        cs = (cs === 'Close') ? 'Open' : 'Close' ;
        return cs;
    };

    pr.changeInfo = function() {
        $.ajax({
            url: "{{ url_for('admin.close_cash') }}",
            dataType: 'json',
            data: {
                cash_id: 1
            },
            success: function (msg) {
                return msg;
            }
        });
    };

    pub.setHandlers = function(){
        $('[data-cash-id]').click(function(evData){
            var cash_id = evData.target.attributes['data-cash-id'].value;
            var cash_state = evData.target.outerText;
            pr.changeState(cash_state);
        })
    };

    return pub;
})

//
// var cash_id = $('[data-cash-id]').click(function(){
//               return $('[data-cash-id]').attr('data-cash-id');
//            });
//
//            $('[data-cash-id]').click(function(){
//                $.ajax({
//                    url: '{{ url_for('admin.close_cash') }}',
//                    data: {
//                        cash_id: 1
//                    },
//                    success: function (msg) {
//                        console.log(msg.user);
//                    },
//                    dataType: 'json'
//                });
//            })
//
//        })

var ChangeUser = (function(){

            var pub = {},
                pr = {};

            pr.data = {
                id:'',
                state: 0,
            };

            pr.insertData = function (attrs) {
                pr.data.id = attrs['data-cash-id'].value;
                pr.data.state = attrs['data-cash-state'].value;
            }


            pr.changeStateClient = function(data) {
                console.log(typeof data.state);
                if (data.state) {
                    pr.button.innerHTML = 'Close';
                    pr.button.className = 'btn btn-xs btn-danger';
                    pr.button.setAttribute('data-cash-state', 1);
                } else {
                    pr.button.innerHTML = 'On';
                    pr.button.className = 'btn btn-xs btn-success';
                    pr.button.setAttribute('data-cash-state', 0);
                }
            };

            pr.changeState = function () {
                $.get({
                    url: "{{ url_for('admin.close_cash') }}",
                    dataType: 'json',
                    data: pr.data,
                    success: function (data) {
                        pr.changeStateClient(data);
                    }
                });
            };

            pub.setHandlers = function(){
                $('[data-cash-id]').click(function(evData) {
                    pr.insertData(evData.target.attributes);
                    pr.button = this;

                    pr.changeState();
                })
            };

            return pub;
        })();

$(document).ready(ChangeUser.setHandlers());

var ChangeUser = (function(){

    var pub = {},
        pr = {};

    pr.url = "{{ url_for('admin.close_cash') }}";

    pr.setBtnToState = function (btn, state) {
        var toClosed = state,
            text = toClosed ? "Close" : "On",
            clsToRemove = toClosed ? "btn-danger" : "btn-success",
            clsToadd = toClosed ? "btn-success" : "btn-danger";

        $(btn).removeClass(clsToRemove);
        $(btn).addClass(clsToadd);
        $(btn).html(text);
        $(btn).attr('data-cash-state', state);
    }

    pr.changeState = function (params, cb) {
        $.get({
            url: pr.url,
            dataType: 'json',
            data: params,
            success: cb
        });
    };

    pub.setHandlers = function(){
        $('[data-cash-id]').click(function(evData) {
            var btn = this,
                attrs = evData.target.attributes;

            data = {
                id: attrs['data-cash-id'].value,
                state: attrs['data-cash-state'].value
            };

            cb = function (params) {
                pr.setBtnToState(btn, params.state);
            };

            pr.changeState(data, cb);
        })
    };

    return pub;
})();






