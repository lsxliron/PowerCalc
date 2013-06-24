$(document).ready(function ()
{
	$("label").click(function()
	{
		alert($("#clientName").val());
	});

	$("#clientSubmit").click(function()
	{
		$.getJSON('/_pc_man',
		{
			clientName:$('input[id=clientName]').val(),
			clientUsername:$('input[id=clientUsername]').val(),
			clientPassword:$('input[id=clientPassword]').val(),
			clientIP:$('input[id=clientIP]').val(),
			clientPort:$('input[id=clientPort]').val(),
			clientOS:$('#clientOS').val()

		},
		function (data)
		{
			//Set ip error message
			if (data.ip_err_msg != "")
			{
				$("#ipErrorMsg").text(data.ip_err_msg);
			} 
			else
			{
				$("#ipErrorMsg").text('');
			}

			//Set port error message
			if (data.port_err_msg != "")
			{
				$("#portErrorMsg").text(data.port_err_msg);
			}
			else
			{
				$("#portErrorMsg").text('');
			}
		
			console.log(data.clientName);
			console.log(data.clientUsername);
			console.log(data.clientPassword);
			console.log(data.clientIP);
			console.log(data.clientPort);
			console.log(data.clientOS);



			//alert($('input[id=clientName]').val());
			
			//$("input[id=clientIP]").val(data.clientUsername);

		});



	});
});
