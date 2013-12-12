require 'cora'
require 'siri_objects'
require 'pp'
require 'net/ssh'
require 'net/scp'
require 'timeout'
require 'mysql'
require 'net/sftp'


class SiriProxy::Plugin::Powercalc < SiriProxy::Plugin
  def initialize(config)
  end


  filter "SetRequestOrigin", direction: :from_iphone do |object|
    puts "[Info - User Location] lat: #{object["properties"]["latitude"]}, long: #{object["properties"]["longitude"]}"
  end

  
  

 

listen_for /Calculate ([a-z]*) ([a-z]*) ([a-z]*) (-*[0-9,]*[0-9].*[0-9])/i do |software, client, function, args|
	
	begin
	#Connect to the database
	client = client.downcase
	con = Mysql.new 'localhost', 'lsxliron', '', 'PowerCalc'
	client_rs = con.query("SELECT * FROM Client WHERE name = '#{client}'")
	client_row = client_rs.fetch_hash
	
	# CLIENTDEFINE VARIABLES
	client_name = client_row["name"]
	client_username = client_row["username"]
	client_pass = client_row["password"]
	client_ip = client_row["IP"]
	client_os = client_row["OS"]
	
	#client_name = client_name.downcase
	puts "client name:\t\t#{client_name}"
	puts "Client username:\t#{client_username}"
	puts "Client password:\t**********"
	puts "Client IP:\t\t#{client_ip}"
	puts "Client O/S:\t\t#{client_os}"
	puts "Function to execute: #{function}(#{args})"

	#DEFINE SOFTWARE VARIABLES	
	sw_rs = con.query("SELECT * FROM Software WHERE client_name = '#{client}' AND name='#{software}'")
	sw_row = sw_rs.fetch_hash

	sw_name = sw_row["name"]
	sw_path = sw_row["path"]

#----------------------------END OF VARIABLE DECLERATION-----------------------

########################
#MATLAB COMMANDS - UNIX#
########################
	if  client_os == "UNIX"
		Thread.new{
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				puts "EXECUTING MATLAB COMMAND"
				#EXECUTE MATLAB PUBLISH
				ssh.exec!(sw_path + " -nodesktop -r \"publish('/Users/"+ client_username + "/Documents/MATLAB/" + function + ".m', struct('codeToEvaluate','" + function + "(" + args + ")', 'showCode', true, 'outputDir', '/Users/" + client_username + "/Documents/MATLAB', 'format','pdf')); exit\"")		
			end
			Net::SCP.start(client_ip, client_username, :password=>client_pass) do |scp|
				#UPLOAD FILE TO THE SERVER AND REMOVE IT FROM THE CLIENT
				puts "DEBUG: COPYING FILE TO SERVER "	
				scp.download!("/Users/" + client_username + "/Documents/MATLAB/" + function + ".pdf", Dir.home + "/PowerCalcTempFiles/temp.pdf")
				#puts "AFTER COPY"		
			end

			#SERVER TASKS
			#CREATE FILE TO CONTIAIN EMAIL DATA
			puts "DEBUG: SETTING UP EMAIL PARAMETERS"
			subject = "Your results for " + function 
			body = "<h2> The attached file is your matlab published file</h2><br><h3>Produced by PowerCalc</h3>"
	

			dataFile = File.new(Dir.home + "/PowerCalcTempFiles/tempData.txt", "w")
			dataFile.puts(body)
			dataFile.close()

			dataFileSubject = File.new(Dir.home + "/PowerCalcTempFiles/tempDataSubject.txt", "w")
			dataFileSubject.puts(subject)  
			dataFileSubject.close
		
			puts "DEBUG: SENDING EMAIL"
			system "python " + Dir.home + "/Desktop/sp/sp-mint/fPowerCalc/sendEmailSiriproxy.py"
			#system "python sendEmailSiriproxy.py"	

			#REMOVING FILE FROM REMOTE CLIENT
			puts "DEBUG: REMOVING FILE FROM REMOTE CLIENT"
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("rm /Users/" + client_username + "/Documents/MATLAB/temp.pdf")
			end
			puts "DEBUG: DONE! SERVER IS READY FOR NEW REQUESTS"
	
		}
	

		say "The result will be sent to your email soon."
		request_completed	

###########################
#MATLAB COMMANDS - WINDOWS#
###########################

	elsif  client_os == "WINDOWS"
		Thread.new{
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				#EXECUTE MATLAB PUBLISH
				puts "DEBUG: CONNECTED TO REMOTE COMPUTER\n"
				ssh.exec!("#{sw_path} -nodesktop -r \"publish('#{function}.m', struct('codeToEvaluate','#{function}(#{ args})', 'showCode', true, 'outputDir', 'C:\\PCTemp', 'format','pdf')); exit\"")
				puts "DEBUG: EXECUTED MATLAB COMMAND"
			end

			Net::SFTP.start(client_ip, client_username, :password=>client_pass) do |sftp|
			#UPLOAD FILE TO THE SERVER AND REMOVE IT FROM THE CLIENT
			# IN WINDOWS SSH:NET DOES NOT WAIT UNTIL MATLAB FINISHED EXECUTION
			# THE SOLUTION IS TO UPLOAD THE FILE TWICE IN 5 SECONDS INTERVAL AND CHECL THE SIZE	
	
				fileReady = false
		
				begin  #WHILE LOOP
					begin  #EXCEPTION HANDLER
						sftp.stat!(function + ".pdf") do |response|
							puts "DEBUG: SETTING THE FLAG"
							fileReady = true
							puts "DEBUG: FLAG IS SET TO TRUE"
						end
					rescue Exception 
						sleep 3
						fileReady = false
						puts "DEBUG: EXCEPTION CAUGHT, FLAG IS FALSE AGAIN"
					end

					if (fileReady == true)
						sftp.download!(function + ".pdf", Dir.home + "/PowerCalcTempFiles/sample1.pdf")
							sleep 15 # AVARAGE TIME TO GENERATE PDF FILE
							sftp.download!(function + ".pdf", Dir.home + "/PowerCalcTempFiles/temp.pdf")
							puts "DEBUG: COMPLETE FILE COPIED"
					end
				end while fileReady == false
			end

			#SERVER TASKS
			#CREATE FILE TO CONTIAIN EMAIL DATA
			subject = "Your results for " + function 
			body = "<h2> The attached file is your matlab published file</h2><br><h3>Produced by PowerCalc</h3>"

			dataFile = File.new(Dir.home + "/PowerCalcTempFiles/tempData.txt", "w")
			dataFile.puts(body)
			dataFile.close()
			puts "DEBUG: DONE SETTING EMAIL SUBJECT"	
	
			dataFileSubject = File.new(Dir.home + "/PowerCalcTempFiles/tempDataSubject.txt", "w")
			dataFileSubject.puts(subject)  
			dataFileSubject.close	
			puts "DEBUG: DONE SETTING EMAIL BODY"
	
			puts "DEBUG: SENDING EMAIL TO USER"	
			system "python " + Dir.home + "/Desktop/sp/sp-mint/fPowerCalc/sendEmailSiriproxy.py"
			#system "python ~/Desktop/sp/sp-mint/fPowerCalc/sendEmailSiriproxy.py"	
			puts "DEBUG: REMOVING FILE FROM REMOTE CLIENT"

			#REMOVE FILE FROM REMOTE CLINET
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("del temp.pdf")
			end
			puts "DEBUG: DONE! SERVER IS READY FOR NEW REQUESTS"

			
		}
	

		say "The result will be sent to your email soon."
		request_completed		

		end	


	#ERROR HANDLING
	rescue Mysql::Error => e
	puts e.errno
	puts e.error

	ensure 
		con.close if con
	end

end



listen_for /Capture image from ([a-z]*)/i do |client|
	
	begin	
		#Connect to the database
		client = client.downcase
		con = Mysql.new 'localhost', 'lsxliron', '', 'PowerCalc'
		client_rs = con.query("SELECT * FROM Client WHERE name = '#{client}'")
		client_row = client_rs.fetch_hash
	
		# CLIENTDEFINE VARIABLES
		client_name = client_row["name"]
		client_username = client_row["username"]
		client_pass = client_row["password"]
		client_ip = client_row["IP"]
		client_os = client_row["OS"]

		#CHOOSE SERVICE
		if client_os == "UNIX"
			software = "imagesnap"
		elsif client_os == "WINDOWS"
			software = "commandcam"	
		end


#----------------------------END OF VARIABLES DECLERATION-----------------------

##########################
#SNAPSHOT COMMANDS - UNIX#
##########################
		#CASE THE CLIENT IS UNIX
		if (client_os == "UNIX")
			Thread.new{
	
			#TAKE A SNAPSHOT
			puts "\n\nDEBUG: TAKING A SNAPSHOT"
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("/usr/local/bin/imagesnap /Users/" + client_username + "/Desktop/snap.jpeg")
			end

			#COPY FILE FROM CLIENT TO SERVER
			puts "DEBUG: COPYING FILE FROM REMOTE CLIENT"
			Net::SCP.start(client_ip, client_username, :password=>client_pass) do |scp|
				scp.download!("/Users/" + client_username + "/Desktop/snap.jpeg", Dir.home + "/PowerCalcTempFiles/snap.jpeg")
			end

			#SEND EMAIL TO USER
			puts "SETTING UP EMAIL PARAMETES"
			subject = "Your snapshot for " + client_name 
			body = "<h2> The attached file is a snapshot from your #{client_name}</h2><br><h3>Produced by PowerCalc</h3>"

			dataFile = File.new(Dir.home + "/PowerCalcTempFiles/tempData.txt", "w")
			dataFile.puts(body)
			dataFile.close()
			puts "DEBUG: \t* DONE SETTING EMAIL SUBJECT"	
	
			dataFileSubject = File.new(Dir.home + "/PowerCalcTempFiles/tempDataSubject.txt", "w")
			dataFileSubject.puts(subject)  
			dataFileSubject.close	
			puts "DEBUG: \t* DONE SETTING EMAIL BODY"
		
			system "python " + Dir.home + "/Desktop/sp/sp-mint/fPowerCalc/sendEmailWithSnapshot.py"
			#system "python sendEmailWithSnapshot.py"
			puts "DEBUG: EMAIL SENT\nDEBUG: REMOVING FILE FROM REMOTE CLIENT"	
		
			#REMOVE FILE FROM REMOTE CLIENT
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("rm /Users/" + client_username + "/Desktop/snap.jpeg")
			end
			
			puts "DEBUG: SERVER IS READY FOR NEW REQUESTS"
			}
	
			say "A snapshot from your #{client_name} will be sent to your email"
			request_completed

		else
#############################
#SNAPSHOT COMMANDS - WINDOWS#
#############################		
			Thread.new{

			#TAKE A SNAPSHOT
			puts "\n\nDEBUG: TAKING A SNAPSHOT"
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("commandcam /filename C:\\PCTemp\\snap.jpeg")
			end
			sleep 5
			#COPY FILE FROM CLIENT TO SERVER
			puts "DEBUG: COPYING FILE FROM REMOTE CLIENT"
			Net::SFTP.start(client_ip, client_username, :password=>client_pass) do |sftp|
				sftp.download!("snap.jpeg", Dir.home + "/PowerCalcTempFiles/snap.jpeg")
			end

			#SEND EMAIL TO USER
			puts "SETTING UP EMAIL PARAMETES"
			subject = "Your snapshot for " + client_name 
			body = "<h2> The attached file is a snapshot from your #{client_name}</h2><br><h3>Produced by PowerCalc</h3>"

			dataFile = File.new(Dir.home + "/PowerCalcTempFiles/tempData.txt", "w")
			dataFile.puts(body)
			dataFile.close()
			puts "DEBUG: \t* DONE SETTING EMAIL SUBJECT"	
	
			dataFileSubject = File.new(Dir.home + "/PowerCalcTempFiles/tempDataSubject.txt", "w")
			dataFileSubject.puts(subject)  
			dataFileSubject.close	
			puts "DEBUG: \t* DONE SETTING EMAIL BODY"
		
			system "python " + Dir.home + "/Desktop/sp/sp-mint/fPowerCalc/sendEmailWithSnapshot.py"
			#system "python sendEmailWithSnapshot.py"
			puts "DEBUG: EMAIL SENT\nDEBUG: REMOVING FILE FROM REMOTE CLIENT"	
			#REMOVE FILE FROM REMOTE CLIENT
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("del C:\\PCTemp\\snap.jpeg")
			end

			puts "DEBUG: SERVER IS READY FOR NEW REQUESTS"

			}

			say "A snapshot from your #{client_name} will be sent to your email"
			request_completed


		end

	rescue Mysql::Error => e
	puts e.errno
	puts e.error

	ensure 
		con.close if con
	end

end	
end
