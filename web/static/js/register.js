var s = false; //true->profesores / false->alumnos
var send = [false,false,false,false,false] ;

check_str('errorName','formName',0);
check_str('errorLastname','formLastname',1);
check_ta();
check_username();
check_password();


function change(ns, str1, str2){
	if(ns != s){
		var change1 = document.getElementById(str1);
		var change2 = document.getElementById(str2);
		change1.classList.remove("unselected");
		change2.classList.remove("selected");
		change1.classList.add("selected");
		change2.classList.add("unselected");
		s = ns;
	}

	var registerform = document.getElementById("formData");
	registerform.action="/students";
	if(s){
		registerform.action = "/teachers";
		document.getElementById("ta").classList.remove("invisible");
	}
	else{
		document.getElementById("ta").classList.add("invisible");
	}

}

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


function check_username(){
	elem = document.getElementById('errorUsername');
	str = document.getElementById('formUsername').value;
	$.getJSON('/users/'+str, function(data){
		if(data.student && data.teacher){
			elem.style.display = 'none';
			send[3] = true;
		}
		else{
			elem.style.display = 'block';
			send[3] = false
		}
	});
}


function check_password(){
	var elem = document.getElementById('errorPassword');
	var str = document.getElementById('formPassword').value;
	if(/([^a-zA-Z\d])+([a-zA-Z\d])+|([a-zA-Z\d])+([^a-zA-Z\d])+/.test(str) && str.length > 4 && str.length <= 50){
		send[4] = true;
		elem.style.display = 'none';
		return;
	}
	elem.style.display = 'block';
	send[4]=false;
}


function submit_form(){
	for(var i = 0; i<5; i++)
		if(!send[i] && !(!s && i == 2))
			return alert("Por favor complete adecuadamente todos los casilleros.");
	return document.getElementById("formData").submit();
}
