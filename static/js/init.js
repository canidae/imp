$(function() {
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
                    var searchResultView = new SearchResultView();
                    searchResultView.render(msg.tracks);
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
        render: function(tracks) {
            console.log(tracks);
            this.$el.html(_.template($('#template-search_result').html(), {}));
            var output = "";
            var trackTemplate = _.template($('#template-track').html());
            for (var a = 0; a < tracks.length; ++a) {
                var track = trackTemplate({num: a + 1, artist: tracks[a][3], title: tracks[a][4]});
                output += track;
            }
            this.$('#search_result').append(output);
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
                currentTrackTitle.html(msg.title);
                currentTrackArtist.html(msg.artist);
            }).fail(function() {
                console.log(arguments);
            });
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

    var Router = Backbone.Router.extend({
        routes: {
            '': 'home'
        },

        home: function() {
        }
    });

    this.router = new Router();

    var navigationView = new NavigationView();
    navigationView.render();

    var playerView = new PlayerView();
    playerView.render();

    Backbone.history.start();
});
