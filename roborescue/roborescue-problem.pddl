(define (problem roborescue-problem)
	(:domain roborescue)
	(:objects
	
		medic1 - medic
		police1 - police
		civ1 - civilian
		hospital1 hospital2 - hospital
		building1 - building
	)
				
	(:init
	
		; agents
		(at medic1 hospital1)
		(at police1 hospital1)

		(available medic1)
		(empty medic1)
		
		; civilians
		(at civ1 building1)
		
		(alive civ1)
		(at 100 (not (alive civ1))) ; til
		(buried civ1)
		
		(= (buriedness civ1) 7)
	
		; graph	
		(blocked-edge hospital1 building1)
		(blocked-edge building1 hospital1)
		(blocked-edge hospital2 building1)
		(blocked-edge building1 hospital2)
		
		(= (distance hospital1 building1) 50)
		(= (distance building1 hospital1) 50)
		(= (distance building1 hospital2) 15)
		(= (distance hospital2 building1) 15)

		(= (blockedness hospital1 building1) 5)
		(= (blockedness building1 hospital1) 5)
		(= (blockedness hospital2 building1) 20)
		(= (blockedness building1 hospital2) 20)
		
		
	)
	
	(:goal (and
			(preference r1 (rescued civ1))
	))
	
	(:metric minimize (+ 
		(total-time)
		(* 1000 (is-violated r1))
	))
)
