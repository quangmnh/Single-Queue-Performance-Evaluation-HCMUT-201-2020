import simpy
import random

class Job:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

class Server:
    def __init__(self, env):
        self.Jobs = list(())
        env.process( self.serve(env) )

    def serve(self, env):
        while True:
            ''' do nothing, just change server to idle
              and then yield a wait event which takes infinite time
            '''
            if len( self.Jobs ) == 0 :
                self.serversleeping = env.process( self.waiting( env ))
                yield self.serversleeping
            else:
                ''' get the first job to be served'''
                j = self.Jobs.pop( 0 )
                ''' yield an event for the job finish'''
                yield env.timeout( j.duration )

    def waiting(self, env):
        try:
            print( 'Server is idle at %d' % env.now )
            yield env.timeout(1000)
        except simpy.Interrupt as i:
            print('A new job comes. Server back to work at %d'
                  ' by \'%s\''% (env.now, i.cause) )

class JobGenerator:
    job_count = 0

    def __init__(self, env, server):
        self.server = server
        env.process( self.jobgen(env) )

    def jobgen(self, env):
        while True:
            '''yield an event for new job arrival'''
            job_interarrival = random.randint(1,5)
            yield env.timeout( job_interarrival )

            ''' generate service time and add job to the list'''
            job_duration = random.randint(2,5)
            self.job_count += 1
            self.server.Jobs.append( Job('Job %s' %self.job_count, job_duration) )
            print( 'job %d: t = %d, l = %d' %( self.job_count, env.now, job_duration ) )

            ''' if server is idle, wake it up'''
            if not self.server.serversleeping.triggered:
                self.server.serversleeping.interrupt( 'Wake up, please.' )

env = simpy.Environment()
MyServer = Server( env )
MyJobGenerator = JobGenerator( env, MyServer )
env.run( until = 20 )
