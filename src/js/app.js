"use strict";

var app = {

    self: null,
    vars: {
        api: 'http://envyc.com:8888/api/',
        kp_posters: 'http://st.kp.yandex.net/images/',
        defaultController: 'index'
    },
    controller: null,
    o: {},

    run: function () {

        var self = this;
        self.getController();
        
        switch (self.controller) {
        
            case 'index': {}
            default: {
            
                self.o.films.getTop().done(function(){

                    var output = '',
                        data = app.cache.data.films,
                        normal = app.cache.data.normal;
                    
                    for (var i = 0; i < data.length; i++) {
                    
                        output += '<li class="clearfix" data-action="film" data-id="' + data[i].kp_id + '">\
                            <div class="poster"><img width="60px" src="' + self.vars.kp_posters + data[i].kp_poster + '"></div>\
                            <div class="description">\
                                <h3>' + data[i].titleRu + 
                                    '<span class="year">' + data[i].year + '</span>\
                                    <span class="rating ' + (data[i].vk_views - data[i].vk_views_prev >= normal ? 'up' : 'down') + '">' + (data[i].vk_views - data[i].vk_views_prev >= normal ? '↑' : '↓') + '</span>\
                                </h3>\
                                <span class="title-en">' + data[i].titleEn + '</span>\
                                <div class="info">' + data[i].genre + '</div>\
                                <div class="about">' + data[i].description + '</div>\
                            </div>\
                        </li>' ;
                    
                    }
                    
                    $('[data-id=top-list]').html(output);
                    
                    $('[data-action=film][data-id]').on('click', function () {
                    
                        var obj = $(this),
                            id = obj.attr('data-id');
                            
                        location.href = 'http://www.kinopoisk.ru/film/' + id;
                        
                        return false;
                    
                    });
                    
                });
            
            }
        
        }

    },
    
    getController: function () {

        var u = location.href.split('/') ;
        this.controller = u[3] || this.vars.defaultController;
        
        return;

    },
    
    cache: {
    
        _set: function (key, value) {

            this[key] = value;
        
        }
    
    }

}

$(function(){

    app.run();

});
