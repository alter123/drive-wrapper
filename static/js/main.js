
$(function(){
    $('.menu-toggle, .menu-close').on('click', function(e){
      e.preventDefault();
      $('.menu').toggleClass('min');
    });
  });

  $(document).ready(function() {
    namespace = '/tasks';

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var _fetch ;

    socket.on('connect', function() {
      console.log('connected');
    });

    socket.on('job_id', function(msg){
      _fetch = setInterval(fetch, 100, msg.data);
    });

    function fetch(job_id) {
      socket.emit('status', { 'job_id': job_id });
    }

    socket.on('fetching', function(msg) {
      if( msg.data == 'True' ){
        clearInterval(_fetch);
        article =  JSON.parse(msg.article);

        if( article.title ){
          var row = "<a id='back' style='cursor:pointer;'> BACK </a></br><br/>" +
          "<h6>" + article.section_name + "</h6><br/>" +
          "<h3>" + article.title + "</h3> <br/>" +
          "<br/><hr/>" +
          "<h5>" + article.author + "</h5> <br/>" +
          "<h6>" + article.publish_date + "</h6> <br/>" +
          "<h6>" + article.modified_date + "</h6> <br/> <br/>"+
          "<h5>" + article.description + "</h5> <br/>"+
          "<p>" + article.content + "</p>" +
          "<hr/> &copy; The Hindu"
        } else {
            var row = "";
            for( var i in article.list ){
                row += "<thead><tr><th>" + article.list[i].head.toUpperCase() 
                  + "</th></tr></thead><tbody>";
                for( var k in article.list[i].link ){
                    row += "<tr><td style='cursor:pointer;' class='idc' id='"+
                            article.list[i].link[k].id 
                    + "'>" + article.list[i].link[k].title.toUpperCase() + "</td></tr>"; 
                }
                row += "</tbody>"
            }
          }
          $('#content').html(row);

          $('td.idc').click(function() { 
              var id = $(this).attr('id');
              socket.emit('search', {data: id});
              return false;
          });

          $('#back').click(function() { 
            socket.emit('back');
            return false;
        });
        }
    });
  });