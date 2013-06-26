$(document).ready(function ()
{
	$("label").click(function()
	{
		alert($("#clientName").val());
	});

	//VALIDATE CLIENT BEFORE ADDING TO THE DB	
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
			else if (data.general_err != "")
			{
				$("#ipErrorMsg").text(data.general_err);
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
			if (data.success_msg == '0')
			{
				$("#clientSuccessSpan").text('Client added successfuly.')
			}
			else
			{
				$("#clientSuccessSpan").text('')
			}
			
			//alert($('input[id=clientName]').val());
			
			//$("input[id=clientIP]").val(data.clientUsername);

		})
	});
	
	//adds a software to the database
	$("#swSubmit").click(function()
	{
		$.getJSON('/_pc_man_add_sw',
		{
			softwareName:$("#softwareName").val(),
			clientName:$("#softwareClient").val(),
			softwarePath:$("#softwarePath").val()
		},
		function(data)
		{

		});

		
	});


	//Enables and disables the software version dropdown list
	$("#softwareClient").change(function()
	{
		$.getJSON('/_pc_man_sw',
		{
			clientName:$("#softwareClient").val()
		},
		function(data)
		{
			console.log(data.os);
			if (data.os == "WINDOWS")
			{
				$("#softwarePath").attr('disabled',true);
			}
			else
			{
				$("#softwarePath").attr('disabled',false);	
			}

		});
	});



	//});
});
