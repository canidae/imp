/* variables */
var searchResult = [];
var playQueue = [];

/* views */
var NavigationView = Backbone.View.extend({
    el: '#header',
    events: {
        "keypress #search_box": "searchKeypress"
    },
    render: function() {
        var template = _.template($('#template-navigation').html(), {});
        this.$el.html(template);
    },

    searchKeypress: function(ev) {
        if (ev.keyCode === 13) {
            var text = this.$el.find("#search_box")[0].value;
            $.ajax({
                url: "searchTrack/" + text
            }).done(function(msg) {
                searchResult = msg.tracks;
                var searchResultView = new SearchResultView();
                searchResultView.render();
            }).fail(function() {
                console.log(arguments);
            });
        }
    }
});

var SearchResultView = Backbone.View.extend({
    el: '#content',
    events: {
    },
    render: function() {
        $('.nav li').removeClass("active");
        $('#nav-search').addClass("active");
        this.$el.html(_.template($('#template-search_result').html(), {}));
        var output = "";
        var trackTemplate = _.template($('#template-track').html());
        for (var a = 0; a < searchResult.length; ++a) {
            var track = searchResult[a];
            output += trackTemplate({num: a + 1, member_id: track[0], track_id: track[1], artist: track[3], title: track[4]});
        }
        this.$('#search_result').append(output);
    }
});

var QueueAndHistoryView = Backbone.View.extend({
    el: '#content',
    events: {
    },
    render: function() {
        $('.nav li').removeClass("active");
        $('#nav-queue_history').addClass("active");
        this.$el.html(_.template($('#template-queue_and_history').html(), {}));
    }
});

var UploadView = Backbone.View.extend({
    el: '#content',
    events: {
    },
    render: function() {
        $('.nav li').removeClass("active");
        $('#nav-upload').addClass("active");
        this.$el.html(_.template($('#template-upload').html(), {}));
    }
});

var PlayerView = Backbone.View.extend({
    el: '#footer',
    events: {
        "click #play_button": "playPause",
        "click #next_button": "playerStop"
    },
    render: function() {
        var template = _.template($('#template-player').html(), {});
        this.$el.html(template);

        // events from player will not propagate
        this.$el.find("#player").on("ended", $.proxy(this.playerStop, this));
        this.$el.find("#player").on("timeupdate", $.proxy(this.playerUpdateTime, this));
        this.$el.find("#player").on("durationchange", $.proxy(this.playerDurationChange, this));

        // start a song
        //this.playerStop();
    },

    playPause: function(ev) {
        var player = this.$el.find("#player")[0];
        var icon = $(ev.currentTarget).find(".glyphicon");
        if (player.paused) {
            player.play();
            icon.removeClass("glyphicon-play");
            icon.addClass("glyphicon-pause");
        } else {
            player.pause();
            icon.removeClass("glyphicon-pause");
            icon.addClass("glyphicon-play");
        }
    },

    playerStop: function() {
        console.log("Queue:");
        for (var a = 0; a < playQueue.length; ++a)
            console.log(playQueue[a][3] + " - " + playQueue[a][4]);
        if (playQueue.length > 0) {
            var player = this.$el.find("#player");
            var source1 = player.find("#source_1");
            var source2 = player.find("#source_2");
            var track = playQueue.shift();
            source1[0].src = "/playTrack/" + track[0] + "/" + track[1] + "/" + "1" + "/" + track[2];
            player[0].load();
            player[0].play();
            var icon = this.$el.find("#play_button .glyphicon");
            icon.removeClass("glyphicon-play");
            icon.addClass("glyphicon-pause");

            // update current/previous
            var currentTrackTitle = this.$el.find("#current_track_title");
            var currentTrackArtist = this.$el.find("#current_track_artist");
            this.$el.find("#previous_track_title").html(currentTrackTitle.html());
            this.$el.find("#previous_track_artist").html(currentTrackArtist.html());
            currentTrackTitle.html(track[3]);
            currentTrackArtist.html(track[4]);
        } else {
            /* blergh, need to clean this up */
            var that = this;
            $.ajax({
                url: "randomTrack"
            }).done(function(msg) {
                var player = that.$el.find("#player");
                var source1 = player.find("#source_1");
                var source2 = player.find("#source_2");
                source1[0].src = "/playTrack/" + msg.track[0] + "/" + msg.track[1] + "/" + "1" + "/" + msg.track[2];
                player[0].load();
                player[0].play();
                var icon = that.$el.find("#play_button .glyphicon");
                icon.removeClass("glyphicon-play");
                icon.addClass("glyphicon-pause");

                // update current/previous
                var currentTrackTitle = that.$el.find("#current_track_title");
                var currentTrackArtist = that.$el.find("#current_track_artist");
                that.$el.find("#previous_track_title").html(currentTrackTitle.html());
                that.$el.find("#previous_track_artist").html(currentTrackArtist.html());
                currentTrackTitle.html(msg.track[3]);
                currentTrackArtist.html(msg.track[4]);
            }).fail(function() {
                console.log(arguments);
            });
        }
    },

    playerUpdateTime: function() {
        var player = this.$el.find("#player")[0];
        var seconds = Math.floor(player.currentTime);
        if (isNaN(seconds))
            seconds = 0;
        var minutes = Math.floor(seconds / 60);
        seconds = seconds % 60;
        var playTime = this.$el.find("#current_time");
        playTime.text((minutes <= 9 ? "0" : "") + minutes + ":" + (seconds <= 9 ? "0" : "") + seconds);
        var playProgress = this.$el.find("#play_progress");
        var progress = player.currentTime / player.duration;
        if (isNaN(progress))
            progress = 0;
        playProgress.attr("value", progress);
        playProgress.text(Math.floor(progress * 100) + "%");

        if (player.duration - player.currentTime < 5 && playQueue.length == 0) {
            $.ajax({
                url: "randomTrack"
            }).done(function(msg) {
                playQueue.push(msg.track);
            }).fail(function() {
                console.log(arguments);
            });
        }
    },

    playerDurationChange: function() {
        var player = this.$el.find("#player")[0];
        var seconds = Math.floor(player.duration);
        if (isNaN(seconds))
            seconds = 0;
        var minutes = Math.floor(seconds / 60);
        seconds = seconds % 60;
        var totalTime = this.$el.find("#total_time");
        totalTime.text((minutes <= 9 ? "0" : "") + minutes + ":" + (seconds <= 9 ? "0" : "") + seconds);
    }
});

/* routing */
var Router = Backbone.Router.extend({
    routes: {
        '': 'queue',
        'search': 'search',
        'queue': 'queue',
        'upload': 'upload'
    },

    search: function() {
        var searchResultView = new SearchResultView();
        searchResultView.render();
    },

    queue: function() {
        var queueAndHistoryView = new QueueAndHistoryView();
        queueAndHistoryView.render();
    },

    upload: function() {
        var uploadView = new UploadView();
        uploadView.render();
    }
});

/* functions */


/* "main": executed after page is done loading */
$(function() {
    this.router = new Router();

    var navigationView = new NavigationView();
    navigationView.render();

    var playerView = new PlayerView();
    playerView.render();

    var queueAndHistoryView = new QueueAndHistoryView();
    queueAndHistoryView.render();

    Backbone.history.start();
});
