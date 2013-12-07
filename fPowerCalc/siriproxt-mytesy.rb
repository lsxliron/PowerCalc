require 'cora'
require 'siri_objects'
require 'pp'
require 'net/ssh'
require 'net/scp'
require 'timeout'
require 'mysql'
require 'net/sftp'

#######
# This is a "hello world" style plugin. It simply intercepts the phrase "test siri proxy" and responds
# with a message about the proxy being up and running (along with a couple other core features). This
# is good base code for other plugins.
#
# Remember to add other plugins to the "config.yml" file if you create them!
######

class SiriProxy::Plugin::Mytest < SiriProxy::Plugin
  def initialize(config)
    #if you have custom configuration options, process them here!
  end

  #get the user's location and display it in the logs
  #filters are still in their early stages. Their interface may be modified
  filter "SetRequestOrigin", direction: :from_iphone do |object|
    puts "[Info - User Location] lat: #{object["properties"]["latitude"]}, long: #{object["properties"]["longitude"]}"

    #Note about returns from filters:
    # - Return false to stop the object from being forwarded
    # - Return a Hash to substitute or update the object
    # - Return nil (or anything not a Hash or false) to have the object forwarded (along with any
    #    modifications made to it)
  end

  listen_for /where am i/i do
    say "Your location is: #{location.address}"
  end

  #JUST FOR TESTING#####
  listen_for /show me/i do
    ss = String.new
    File.open('1.txt').each_line{|s| ss=ss+s}
    add_views = SiriAddViews.new
    add_views.make_root(last_ref_id)
    utterance = SiriAssistantUtteranceView.new("#{ss}")
    add_views.views << utterance
    say "look at your screen" 
    send_object add_views
    system "~/Desktop/ls"
    system "python  sendEmail.py"
request_completed
  end


  #JUST FOR TESTING#####
  listen_for /Take a snapshot from my server/i do
    system "sudo -u lsxliron streamer -f jpeg -o /home/lsxliron/Desktop/temp.jpeg"
    system "sudo -u lsxliron python ~/Desktop/1.py"
    system "sudo rm -u lsxlirn rm ~/Desktop/temp.jpeg"
    say "An email was sent to your inbox"
    request_completed
end

    listen_for /Testing ([0-9,]*[0-9]), ([0-9,]*[0-9])/i do |numbera, numberb|
	say "Invoking Matlab on remote computer, please check your email in a couple of minutes."
	Thread.new{
	begin

		Net::SSH.start('192.168.1.32','lsxliron',:password=>'1qaz') do |ssh|

			ssh.exec!("cd /Users/lsxliron/Desktop;/Applications/MATLAB_R2012a.app/bin/matlab -nodesktop -nosplash -noawt -r \"publish	('test.m',struct('codeToEvaluate','test(#{numbera},#{numberb})','showCode',false,'outputDir','/Users/lsxliron/Desktop','format','pdf'))\",exit") 

		end

	
		Net::SCP.start('192.168.1.32','lsxliron',:password=>'1qaz')do |scp|
			puts "Started file upload"
			scp.download!("/Users/lsxliron/Desktop/test.pdf","/home/lsxliron/Desktop/temp.pdf")
		end
		system "sudo -u lsxliron python /home/lsxliron/Desktop/1.py"
		system "sudo -u lsxliron rm /home/lsxliron/Desktop/temp.pdf"
       		Net::SSH.start('192.168.1.32','lsxliron',:password=>'1qaz')do |ssh|
        		ssh.exec("rm -Q /Users/lsxliron/Desktop/test.pdf")
        	end
	
   		say "An email sent to your inbox"
    		system "sudo -u lsxliron rm /home/lsxliron/Desktop/temp.pdf"
	rescue 
	say "An error occured, please try again"
	
	ensure
	request_completed
	end
	}
	request_completed
    end

#################
#TESTS FOR MYSQL#
#################

listen_for /Calculate ([a-z]*) ([a-z]*) ([a-z]*) ([0-9,]*[0-9].*[0-9])/i do |software, client, function, args|
	
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

#----------------------------END OF VARS-----------------------

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
			system "python " + Dir.home + "/Desktop/sp2test/sp1-nb/fPowerCalc/sendEmailSiriproxy.py"

			#REMOVING FILE FROM REMOTE CLIENT
			puts "DEBUG: REMOVING FILE FROM REMOTE CLIENT"
			Net::SSH.start(client_ip, client_username,:password=>client_pass) do |ssh|
				ssh.exec!("rm /Users/" + client_username + "/Documents/MATLAB/temp.pdf")
			end
			puts "DEBUG: DONE! SERVER IS READY FOR NEW REQUESTS"
	
		}
	

		say "The result will be sent to your email soon."
		request_completed	


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
			system "python " + Dir.home + "/Desktop/sp2test/sp1-nb/fPowerCalc/sendEmailSiriproxy.py"

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

################################################################
#----------------------------END OF VARS-----------------------#
################################################################

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
		
			system "python " + Dir.home + "/Desktop/sp2test/sp1-nb/fPowerCalc/sendEmailWithSnapshot.py"
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
			#WINDOWS MACHINCES
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
		
			system "python " + Dir.home + "/Desktop/sp2test/sp1-nb/fPowerCalc/sendEmailWithSnapshot.py"
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

	









  listen_for /test siri proxy/i do
    say "Siri Proxy is up and running!" #say something to the user!

    request_completed #always complete your request! Otherwise the phone will "spin" at the user!
  end

  #Demonstrate that you can have Siri say one thing and write another"!
  listen_for /you don't say/i do
    say "Sometimes I don't write what I say", spoken: "Sometimes I don't say what I write"
  end

  #demonstrate state change
  listen_for /siri proxy test state/i do
    set_state :some_state #set a state... this is useful when you want to change how you respond after certain conditions are met!
    say "I set the state, try saying 'confirm state change'"

    request_completed #always complete your request! Otherwise the phone will "spin" at the user!
  end

  listen_for /confirm state change/i, within_state: :some_state do #this only gets processed if you're within the :some_state state!
    say "State change works fine!"
    set_state nil #clear out the state!

    request_completed #always complete your request! Otherwise the phone will "spin" at the user!
  end

  #demonstrate asking a question
  listen_for /siri proxy test question/i do
    response = ask "Is this thing working?" #ask the user for something

    if(response =~ /yes/i) #process their response
      say "Great!"
    else
      say "You could have just said 'yes'!"
    end

    request_completed #always complete your request! Otherwise the phone will "spin" at the user!
  end

  #demonstrate capturing data from the user (e.x. "Siri proxy number 15")
  listen_for /siri proxy number ([0-9,]*[0-9])/i do |number|
    say "Detected number: #{number}"

    request_completed #always complete your request! Otherwise the phone will "spin" at the user!
  end

  #demonstrate injection of more complex objects without shortcut methods.
  listen_for /test map/i do
    add_views = SiriAddViews.new
    add_views.make_root(last_ref_id)
    map_snippet = SiriMapItemSnippet.new
    map_snippet.items << SiriMapItem.new
    utterance = SiriAssistantUtteranceView.new("Testing map injection!")
    add_views.views << utterance
    add_views.views << map_snippet
    
    #you can also do "send_object object, target: :guzzoni" in order to send an object to guzzoni
    send_object add_views #send_object takes a hash or a SiriObject object

    request_completed #always complete your request! Otherwise the phone will "spin" at the user!
  end
end
