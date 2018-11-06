//update Information

var modal = document.getElementById('update');

function show_update(){
	modal.style.display = 'block';
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
    if (event.target == modal2) {
        modal2.style.display = "none";
    }
}

send = [true,true,true];

function check_str(id1, id2, i){
	var elem = document.getElementById(id1);
	var inp = document.getElementById(id2);
	var str = inp.value;
	if(!/[^a-zA-Z]/.test(str) && str.length > 0 && str.length <= 50){
		send[i] = true;
		elem.style.display = 'none';
		return;
	}
	elem.style.display = 'block';
	send[i]=false;
}

function check_ta(){
	var elem = document.getElementById('errorta');
	var inp = document.getElementById('ta');
	var str = inp.value;
	if(str.length > 50 && str.length <= 500){
		send[2] = true;
		elem.style.display = 'none';
		return;
	}
	elem.style.display = 'block';
	send[2]=false;
}

function submit_form(){
	for(var i = 0; i<3; i++)
		if(!send[i])
			return alert("Por favor complete adecuadamente todos los casilleros.");
	return document.getElementById("formData").submit();
}

//update profile pic

var pic_state = false;

var modal2 = document.getElementById('profileUpdate');
function show_pic(){
	modal2.style.display = 'block';
}

function validate(input){
    var URL = window.URL || window.webkitURL;
    var file = input.files[0];
    if (file) {
        var image = new Image();
        image.onload = function() {
            if (this.width) {
                pic_state = true;
            }
            else{
            	pic_state = false;
            	alert("Por favor ingrese una imagen válida.")
            }
        };
        image.src = URL.createObjectURL(file);
        return;
    }
    pic_state = false;
}

function submit_pic(){
	if(pic_state)
		return document.getElementById("formPic").submit();
	alert("Por favor suba una foto válida.")
}


//Ratings

$.fn.stars = function() {
    return $(this).each(function() {
        // Get the value
        var val = parseFloat($(this).html());
        // Make sure that the value is in 0 - 5 range, multiply to get width
        var size = Math.max(0, (Math.min(5, val))) * 16;
        // Create stars holder
        var $span = $('<span />').width(size);
        // Replace the numerical value with stars
        $(this).html($span);
    });
}

//Load Teacher info

teacher_url = "/teachers/" + teacher_id;
subject_url = "/teacher_subject/teacher/" + teacher_id;

$.getJSON(teacher_url, function(teacher){
	$("#teacherName").html(teacher.name + " " + teacher.lastname);
	$("#teacherInformation").html(teacher.information);
	$("#teacherUsername").html(teacher.username);
	if(user_profile){
		$("#formName").val(teacher.name);
		$("#formLastname").val(teacher.lastname);
		$("#ta").html(teacher.information);
	}
	var avgRating = 0;
	if(teacher.numRating == 0)
		avgRating = 5;
	else
		avgRating = teacher.sumRating/teacher.numRating;
	$("#avgRating").html(avgRating);
});

$.getJSON(subject_url, function(subject){
	var temp = "" ;
	$.each(subject, function(i,sub){
		temp = temp + sub.name +", ";
	});
	temp = temp.slice(0, temp.length - 2);
	$("#teacherSubjects").html(temp);
});

$.getJSON('/ratings/teacher/'+teacher_id, function(ratings){
	$.each(ratings, function(i, rat){
		var a = "<div class = 'review'><span class='title'>";
		a = a + rat.title + "</span>"
		a = a + "<div class='ratingProfesor'><span class='stars'>"+rat.value+"</span></div>"
		a = a + "<p>" + rat.content + "</p></div>"
		$("#reviewsProfesor").append(a);
	});
	$('span.stars').stars();
});
