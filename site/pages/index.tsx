import { Layout, Text, Code, Page, Link } from '@vercel/examples-ui'
import Head from 'next/head'

import fs from 'fs';
import path from 'path';

const GamesPlayed = ({ counts } : any) => (
  <div className="flex space-x-4">
    <div className="p-4"><Text variant="description">Games played:</Text></div>
    {counts.map((team) => (
      <div key={team[0]} className="p-4"><Text variant="description">{team[0]}: {team[1]}</Text></div>
    ))}
  </div>
);

const Summary = ({ team_wins, player_points, people } : any) => {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-evenly w-full">
        <table className="border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left p-1">Team</th>
              <th className="text-left p-1">Wins</th>
            </tr>
          </thead>
          <tbody>
            {team_wins.map((record) => (
              <tr key={record.team} className="border-b">
                <td className="p-1">{record.team}</td>
                <td className="p-1">{record.wins}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <table className="border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left p-1">Player</th>
              <th className="text-left p-1">Points</th>
            </tr>
          </thead>
          <tbody>
            {player_points.map((record) => (
              <tr key={record.player} className="border-b">
                <td className="p-1">{record.player}</td>
                <td className="p-1">{record.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

        <table className="border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left p-1">Person</th>
              <th className="text-left p-1">Wins</th>
              <th className="text-left p-1">Points</th>
              <th className="text-left p-1">Total</th>
            </tr>
          </thead>
          <tbody>
            {people.map((person) => (
              <tr key={person.name} className="border-b">
                <td className="p-1">{person.name}</td>
                <td className="p-1">{person.wins}</td>
                <td className="p-1">{person.points}</td>
                <td className="p-1">{person.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
    </div>
  )
};

const Game = ({ game } : any) => {
  const id = game.id;
  const title = game.names[0] + " - " + game.names[1];
  const scores = game.scores ? (game.scores[0] + " - " + game.scores[1]) : "";

  return (
    <div className="flex justify-between items-center border border-gray-100 shadow-md rounded-lg p-5">
      <div className="grid gap-2">
        <a
          href={`https://www.nhl.com/gamecenter/${id}`}
          target="_blank"
          rel="noreferrer noopener"
        >
          <h3 className="text-gray-900 text-lg hover:text-black font-semibold transition-all">
            {title}
          </h3>
        </a>
        {game.goals.map((goal, idx) => (
          <div key={idx} className="flex space-x-1 text-gray-500 text-sm">
            <p>{goal.period}</p>
            <p>{goal.time}</p>
            <p>-</p>
            {goal.players.map((player,idx) => (
              player[1] ?
                 (<p key={idx}><strong>{player[0]}</strong></p>)
                 :
                 (<p key={idx}>{player[0]}</p>)))}
          </div>
        ))}
      </div>
      <h2 className="text-gray-800 text-lg">{scores}</h2>
    </div>
  )
};

export default function Home({ data, player_points, team_wins, people }: any) {
  return (
    <Page>
      <section className="flex flex-col gap-6">
        <Text variant="h1">Playoff Bet Tracker</Text>
        <Text variant="description">Tracking the playoff pool. Players get two points for a win by one of their teams and one point for a point scored by one of their players.</Text>
        <Text variant="body">Lovina: CAR, COL, EDM, TOR, WPG, C. McDavid, K. Connor, L. Draisaitl,  N. Kucherov, N. MacKinnon</Text>
        <Text variant="body">Paul: CAR, COL, FLA, TBL, VGK, B. Point, C. Makar, J. Eichel, N. Kucherov, N. MacKinnon</Text>
        <Text variant="body">Sean: EDM, FLA, VGK, WSH, WPG, C. McDavid, J. Eichel, K. Connor, L. Draisaitl, N. MacKinnon</Text>
        <Text variant="body"></Text>
      </section>
      <section>
        <Summary team_wins={team_wins} player_points={player_points} people={people}/>
      </section>
      <section className="grid gap-6 mt-10 pt-10 border-t border-gray-300">
        <div className="flex flex-col gap-12">
          {data.map((date) => (
            <div key={date.date} className="flex flex-col gap-6">
              <div className="flex justify-between items-center">
                <Text variant="h2">{date.date}</Text>
              </div>
              {date.games.map((game) => (
                <div key={game.id}><Game game={game}/></div>
              ))}
            </div>
          ))}
        </div>
      </section>
    </Page>
  )
}

export async function getStaticProps() {
  const dataPath = path.join(process.cwd(), 'public', 'data.json')
  const contents = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(contents);
  return {
    props: {
      data: data.games.reverse(),
      team_wins: data.team_wins,
      player_points: data.player_points,
      people: data.people,
    },
    revalidate: 60,
  };
}
