"use strict";

app.o.films = {

    getTop: function () {
        
        var d = $.Deferred();
    
        $.ajax({
            url: app.vars.api + 'getTop',
            data: {
                count:20,
                date_from:'16-02-2016',
                date_to:'16-02-2016'
            },
            success: function(data){
                
                app.cache._set('data', data);
                d.resolve();
                
            }
        });
        
        return d.promise();
    
    }

}